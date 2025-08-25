package db

import (
	"context"
	"crypto/md5"
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"golang.org/x/crypto/ssh"
)

type JSONConfig struct {
	UseSSH    bool
	SSHConfig *SSHConfig
}

type SSHConfig struct {
	Host     string
	Port     int
	User     string
	KeyPath  string
	Password string
	Timeout  time.Duration
}

type JSONManager struct {
	filename   string
	config     *JSONConfig
	timeout    time.Duration
	retryDelay time.Duration
	maxRetries int
	sshClient  *ssh.Client
}

func NewJSONManager(filename string, config *JSONConfig) *JSONManager {
	if config == nil {
		config = &JSONConfig{UseSSH: false}
	}
	
	return &JSONManager{
		filename:   filename,
		config:     config,
		timeout:    10 * time.Second,
		retryDelay: 50 * time.Millisecond,
		maxRetries: 200,
	}
}

func (m *JSONManager) WriteJSON(ctx context.Context, data any) error {
	if m.config.UseSSH {
		if err := m.ensureSSHConnection(); err != nil {
			return err
		}
	}

	return m.withLock(ctx, func() error {
		return m.writeJSONAtomic(data)
	})
}

func (m *JSONManager) ReadJSON(ctx context.Context, data any) error {
	if m.config.UseSSH {
		if err := m.ensureSSHConnection(); err != nil {
			return err
		}
	}

	return m.withLock(ctx, func() error {
		return m.readJSON(data)
	})
}

func (m *JSONManager) Exists() (bool, error) {
	if m.config.UseSSH {
		if err := m.ensureSSHConnection(); err != nil {
			return false, err
		}
		return m.sshFileExists(m.filename)
	}
	
	_, err := os.Stat(m.filename)
	return err == nil, nil
}

func (m *JSONManager) Close() error {
	if m.sshClient != nil {
		err := m.sshClient.Close()
		m.sshClient = nil
		return err
	}
	return nil
}

// Generic lock handling
func (m *JSONManager) withLock(ctx context.Context, operation func() error) error {
	lockfile := m.filename + ".lock"
	
	ctx, cancel := context.WithTimeout(ctx, m.timeout)
	defer cancel()
	
	if err := m.acquireLockWithTimeout(ctx, lockfile); err != nil {
		return err
	}
	
	defer func() {
		if err := m.removeLockFile(lockfile); err != nil {
			fmt.Printf("Warning: failed to remove lock file: %v\n", err)
		}
	}()
	
	return operation()
}

func (m *JSONManager) acquireLockWithTimeout(ctx context.Context, lockfile string) error {
	ticker := time.NewTicker(m.retryDelay)
	defer ticker.Stop()
	
	attempts := 0
	for {
		select {
		case <-ctx.Done():
			return fmt.Errorf("timeout acquiring lock after %d attempts: %w", attempts, ctx.Err())
		case <-ticker.C:
			attempts++
			
			if m.config.UseSSH {
				if acquired, err := m.acquireSSHLock(lockfile); err != nil {
					return fmt.Errorf("failed to acquire SSH lock: %w", err)
				} else if acquired {
					return nil
				}
				
				if err := m.cleanOrphanedSSHLock(lockfile); err != nil {
					fmt.Printf("Warning: failed to clean orphaned SSH lock: %v\n", err)
				}
			} else {
				if err := m.acquireLocalLock(lockfile); err == nil {
					return nil
				}
				
				m.cleanOrphanedLocalLock(lockfile)
			}
		}
	}
}

// Local lock operations
func (m *JSONManager) acquireLocalLock(lockfile string) error {
	lockFile, err := os.OpenFile(lockfile, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0666)
	if err != nil {
		return err
	}
	
	fmt.Fprintf(lockFile, "pid: %d\ntime: %s\n", os.Getpid(), time.Now().Format(time.RFC3339))
	lockFile.Close()
	return nil
}

func (m *JSONManager) cleanOrphanedLocalLock(lockfile string) {
	if info, err := os.Stat(lockfile); err == nil {
		if time.Since(info.ModTime()) > m.timeout {
			os.Remove(lockfile)
		}
	}
}

func (m *JSONManager) removeLockFile(lockfile string) error {
	if m.config.UseSSH {
		return m.removeSSHFile(lockfile)
	}
	return os.Remove(lockfile)
}

// Atomic write operations
func (m *JSONManager) writeJSONAtomic(data any) error {
	if m.config.UseSSH {
		return m.writeJSONAtomicSSH(data)
	}
	return m.writeJSONAtomicLocal(data)
}

func (m *JSONManager) writeJSONAtomicLocal(data any) error {
	tempFile := m.filename + ".tmp"
	
	file, err := os.Create(tempFile)
	if err != nil {
		return fmt.Errorf("failed to create temp file: %w", err)
	}
	
	defer func() {
		file.Close()
		if err != nil {
			os.Remove(tempFile)
		}
	}()
	
	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	encoder.SetEscapeHTML(false)
	
	if err = encoder.Encode(data); err != nil {
		return fmt.Errorf("failed to encode JSON: %w", err)
	}
	
	if err = file.Sync(); err != nil {
		return fmt.Errorf("failed to sync file: %w", err)
	}
	
	file.Close()
	
	if err = os.Rename(tempFile, m.filename); err != nil {
		return fmt.Errorf("failed to rename temp file: %w", err)
	}
	
	return nil
}

func (m *JSONManager) writeJSONAtomicSSH(data any) error {
	tempFile := fmt.Sprintf("%s.tmp.%x", m.filename, md5.Sum([]byte(fmt.Sprintf("%d", time.Now().UnixNano()))))
	
	jsonData, err := json.MarshalIndent(data, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal JSON: %w", err)
	}
	
	if err := m.writeSSHFile(tempFile, string(jsonData)); err != nil {
		return fmt.Errorf("failed to write temp file via SSH: %w", err)
	}
	
	if err := m.renameSSHFile(tempFile, m.filename); err != nil {
		m.removeSSHFile(tempFile)
		return fmt.Errorf("failed to rename temp file via SSH: %w", err)
	}
	
	return nil
}

// Read operations
func (m *JSONManager) readJSON(data any) error {
	if m.config.UseSSH {
		return m.readJSONSSH(data)
	}
	return m.readJSONLocal(data)
}

func (m *JSONManager) readJSONLocal(data any) error {
	if _, err := os.Stat(m.filename); os.IsNotExist(err) {
		return fmt.Errorf("file %s does not exist", m.filename)
	}
	
	file, err := os.Open(m.filename)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()
	
	decoder := json.NewDecoder(file)
	decoder.DisallowUnknownFields()
	
	if err := decoder.Decode(data); err != nil {
		return fmt.Errorf("failed to decode JSON: %w", err)
	}
	
	return nil
}

func (m *JSONManager) readJSONSSH(data any) error {
	exists, err := m.sshFileExists(m.filename)
	if err != nil {
		return fmt.Errorf("failed to check file existence: %w", err)
	}
	if !exists {
		return fmt.Errorf("file %s does not exist", m.filename)
	}
	
	content, err := m.readSSHFile(m.filename)
	if err != nil {
		return fmt.Errorf("failed to read file via SSH: %w", err)
	}
	
	if err := json.Unmarshal([]byte(content), data); err != nil {
		return fmt.Errorf("failed to unmarshal JSON: %w", err)
	}
	
	return nil
}

// SSH connection management
func (m *JSONManager) ensureSSHConnection() error {
	if m.sshClient != nil {
		return nil
	}

	if m.config.SSHConfig == nil {
		return fmt.Errorf("SSH config is required when UseSSH is true")
	}

	var auth []ssh.AuthMethod

	if m.config.SSHConfig.KeyPath != "" {
		key, err := os.ReadFile(m.config.SSHConfig.KeyPath)
		if err != nil {
			return fmt.Errorf("failed to read SSH key: %w", err)
		}

		signer, err := ssh.ParsePrivateKey(key)
		if err != nil {
			return fmt.Errorf("failed to parse SSH key: %w", err)
		}
		auth = append(auth, ssh.PublicKeys(signer))
	}

	if m.config.SSHConfig.Password != "" {
		auth = append(auth, ssh.Password(m.config.SSHConfig.Password))
	}

	config := &ssh.ClientConfig{
		User:            m.config.SSHConfig.User,
		Auth:            auth,
		Timeout:         m.config.SSHConfig.Timeout,
		HostKeyCallback: ssh.InsecureIgnoreHostKey(),
	}

	client, err := ssh.Dial("tcp", fmt.Sprintf("%s:%d", m.config.SSHConfig.Host, m.config.SSHConfig.Port), config)
	if err != nil {
		return fmt.Errorf("failed to connect via SSH: %w", err)
	}

	m.sshClient = client
	return nil
}

// SSH lock operations
func (m *JSONManager) acquireSSHLock(lockfile string) (bool, error) {
	exists, err := m.sshFileExists(lockfile)
	if err != nil {
		return false, err
	}
	if exists {
		return false, nil
	}
	
	lockContent := fmt.Sprintf("pid: %s\nhost: %s\ntime: %s\n", 
		m.getProcessID(), m.config.SSHConfig.Host, time.Now().Format(time.RFC3339))
	
	err = m.createSSHFileExclusive(lockfile, lockContent)
	return err == nil, err
}

func (m *JSONManager) cleanOrphanedSSHLock(lockfile string) error {
	info, err := m.getSSHFileInfo(lockfile)
	if err != nil {
		return err
	}
	
	if time.Since(info.ModTime) > m.timeout {
		return m.removeSSHFile(lockfile)
	}
	
	return nil
}

// SSH file operations
func (m *JSONManager) sshFileExists(filename string) (bool, error) {
	session, err := m.sshClient.NewSession()
	if err != nil {
		return false, err
	}
	defer session.Close()
	
	cmd := fmt.Sprintf("test -f %s", m.escapeShellArg(filename))
	err = session.Run(cmd)
	if err != nil {
		if strings.Contains(err.Error(), "exit status 1") {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

func (m *JSONManager) createSSHFileExclusive(filename, content string) error {
	session, err := m.sshClient.NewSession()
	if err != nil {
		return err
	}
	defer session.Close()
	
	cmd := fmt.Sprintf("set -C; echo %s > %s", 
		m.escapeShellArg(content), m.escapeShellArg(filename))
	
	return session.Run(cmd)
}

func (m *JSONManager) writeSSHFile(filename, content string) error {
	session, err := m.sshClient.NewSession()
	if err != nil {
		return err
	}
	defer session.Close()
	
	session.Stdin = strings.NewReader(content)
	cmd := fmt.Sprintf("cat > %s", m.escapeShellArg(filename))
	
	return session.Run(cmd)
}

func (m *JSONManager) readSSHFile(filename string) (string, error) {
	session, err := m.sshClient.NewSession()
	if err != nil {
		return "", err
	}
	defer session.Close()
	
	cmd := fmt.Sprintf("cat %s", m.escapeShellArg(filename))
	output, err := session.Output(cmd)
	if err != nil {
		return "", err
	}
	
	return string(output), nil
}

func (m *JSONManager) renameSSHFile(oldname, newname string) error {
	session, err := m.sshClient.NewSession()
	if err != nil {
		return err
	}
	defer session.Close()
	
	cmd := fmt.Sprintf("mv %s %s", m.escapeShellArg(oldname), m.escapeShellArg(newname))
	return session.Run(cmd)
}

func (m *JSONManager) removeSSHFile(filename string) error {
	session, err := m.sshClient.NewSession()
	if err != nil {
		return err
	}
	defer session.Close()
	
	cmd := fmt.Sprintf("rm -f %s", m.escapeShellArg(filename))
	return session.Run(cmd)
}

type SSHFileInfo struct {
	ModTime time.Time
	Size    int64
}

func (m *JSONManager) getSSHFileInfo(filename string) (*SSHFileInfo, error) {
	session, err := m.sshClient.NewSession()
	if err != nil {
		return nil, err
	}
	defer session.Close()
	
	cmd := fmt.Sprintf("stat -c '%%Y %%s' %s", m.escapeShellArg(filename))
	output, err := session.Output(cmd)
	if err != nil {
		return nil, err
	}
	
	var timestamp, size int64
	if _, err := fmt.Sscanf(string(output), "%d %d", &timestamp, &size); err != nil {
		return nil, fmt.Errorf("failed to parse stat output: %w", err)
	}
	
	return &SSHFileInfo{
		ModTime: time.Unix(timestamp, 0),
		Size:    size,
	}, nil
}

func (m *JSONManager) escapeShellArg(arg string) string {
	return "'" + strings.ReplaceAll(arg, "'", "'\"'\"'") + "'"
}

func (m *JSONManager) getProcessID() string {
	return fmt.Sprintf("%d@%s", os.Getpid(), m.config.SSHConfig.Host)
}

// Legacy compatibility - keeping the old SafeJSONManager interface
type SafeJSONManager struct {
	*JSONManager
}

func NewSafeJSONManager(filename string) *SafeJSONManager {
	return &SafeJSONManager{
		JSONManager: NewJSONManager(filename, &JSONConfig{UseSSH: false}),
	}
}

// Legacy Exists method that returns only bool (not bool, error)
func (s *SafeJSONManager) Exists() bool {
	exists, _ := s.JSONManager.Exists()
	return exists
}
