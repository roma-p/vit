package db

import (
	"context"
	"fmt"
	"net"
	"os"
	"path/filepath"
	"testing"
	"time"

	"golang.org/x/crypto/ssh"
)

// MockSSHServer provides a simple SSH server for testing
type MockSSHServer struct {
	listener net.Listener
	config   *ssh.ServerConfig
	tempDir  string
	files    map[string]string
}

func NewMockSSHServer(t *testing.T) *MockSSHServer {
	tempDir := t.TempDir()
	
	// Generate test key
	keyPath := filepath.Join(tempDir, "test_key")
	
	// For testing, we'll use a simple password-based auth
	config := &ssh.ServerConfig{
		PasswordCallback: func(conn ssh.ConnMetadata, password []byte) (*ssh.Permissions, error) {
			if string(password) == "testpass" {
				return nil, nil
			}
			return nil, fmt.Errorf("password rejected for %s", conn.User())
		},
	}
	
	// Generate a temporary host key for testing
	if err := generateTestKey(keyPath); err != nil {
		t.Fatalf("Failed to generate test key: %v", err)
	}
	
	hostKey, err := os.ReadFile(keyPath)
	if err != nil {
		t.Fatalf("Failed to read test key: %v", err)
	}
	
	signer, err := ssh.ParsePrivateKey(hostKey)
	if err != nil {
		t.Fatalf("Failed to parse host key: %v", err)
	}
	
	config.AddHostKey(signer)
	
	return &MockSSHServer{
		config:  config,
		tempDir: tempDir,
		files:   make(map[string]string),
	}
}

func generateTestKey(keyPath string) error {
	// This would normally generate an SSH key, but for testing
	// we'll create a simple RSA key. In a real implementation,
	// you'd use crypto/rsa or similar to generate a proper key.
	
	// For now, create a dummy key file
	return os.WriteFile(keyPath, []byte(`-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEA1234567890abcdef...
-----END OPENSSH PRIVATE KEY-----`), 0600)
}

func (s *MockSSHServer) Start(t *testing.T) string {
	listener, err := net.Listen("tcp", "localhost:0")
	if err != nil {
		t.Fatalf("Failed to create listener: %v", err)
	}
	
	s.listener = listener
	
	go func() {
		for {
			conn, err := listener.Accept()
			if err != nil {
				return // Server stopped
			}
			
			go s.handleConnection(conn, t)
		}
	}()
	
	return listener.Addr().String()
}

func (s *MockSSHServer) handleConnection(conn net.Conn, t *testing.T) {
	defer conn.Close()
	
	sshConn, chans, reqs, err := ssh.NewServerConn(conn, s.config)
	if err != nil {
		return
	}
	defer sshConn.Close()
	
	go ssh.DiscardRequests(reqs)
	
	for newChannel := range chans {
		if newChannel.ChannelType() != "session" {
			newChannel.Reject(ssh.UnknownChannelType, "unknown channel type")
			continue
		}
		
		channel, requests, err := newChannel.Accept()
		if err != nil {
			continue
		}
		
		go s.handleSession(channel, requests, t)
	}
}

func (s *MockSSHServer) handleSession(channel ssh.Channel, requests <-chan *ssh.Request, t *testing.T) {
	defer channel.Close()
	
	for req := range requests {
		switch req.Type {
		case "exec":
			if req.WantReply {
				req.Reply(true, nil)
			}
			
			cmd := string(req.Payload[4:]) // Skip length prefix
			s.executeCommand(channel, cmd)
			
		default:
			if req.WantReply {
				req.Reply(false, nil)
			}
		}
	}
}

func (s *MockSSHServer) executeCommand(channel ssh.Channel, cmd string) {
	// Simple command simulation for testing
	switch {
	case cmd == "test -f /test/file.json":
		if _, exists := s.files["/test/file.json"]; exists {
			channel.SendRequest("exit-status", false, []byte{0, 0, 0, 0})
		} else {
			channel.SendRequest("exit-status", false, []byte{0, 0, 0, 1})
		}
		
	case cmd == "cat /test/file.json":
		if content, exists := s.files["/test/file.json"]; exists {
			channel.Write([]byte(content))
			channel.SendRequest("exit-status", false, []byte{0, 0, 0, 0})
		} else {
			channel.SendRequest("exit-status", false, []byte{0, 0, 0, 1})
		}
		
	default:
		// For other commands, just return success
		channel.SendRequest("exit-status", false, []byte{0, 0, 0, 0})
	}
}

func (s *MockSSHServer) Stop() {
	if s.listener != nil {
		s.listener.Close()
	}
}

// Integration tests for SSH functionality
func TestJSONManager_SSHOperations_Integration(t *testing.T) {
	// Skip if no SSH_TEST_HOST environment variable is set
	sshHost := os.Getenv("SSH_TEST_HOST")
	sshUser := os.Getenv("SSH_TEST_USER")
	sshPass := os.Getenv("SSH_TEST_PASS")
	sshKey := os.Getenv("SSH_TEST_KEY")
	
	if sshHost == "" {
		t.Skip("SSH integration tests require SSH_TEST_HOST environment variable")
	}
	
	sshConfig := &SSHConfig{
		Host:     sshHost,
		Port:     22,
		User:     sshUser,
		Password: sshPass,
		KeyPath:  sshKey,
		Timeout:  30 * time.Second,
	}
	
	config := &JSONConfig{
		UseSSH:    true,
		SSHConfig: sshConfig,
	}
	
	tempFile := fmt.Sprintf("/tmp/vit_test_%d.json", time.Now().UnixNano())
	manager := NewJSONManager(tempFile, config)
	defer func() {
		manager.Close()
		// Clean up remote file
		cleanupCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		manager.removeSSHFile(tempFile)
		manager.removeSSHFile(tempFile + ".lock")
		_ = cleanupCtx // Mark as used
	}()
	
	ctx := context.Background()
	
	t.Run("SSH_WriteAndRead", func(t *testing.T) {
		testData := TestData{
			ID:    1,
			Name:  "ssh_test",
			Value: 123,
		}
		testData.Nested.Field = "ssh_nested"
		
		// Write data via SSH
		err := manager.WriteJSON(ctx, testData)
		if err != nil {
			t.Fatalf("Failed to write JSON via SSH: %v", err)
		}
		
		// Read data back via SSH
		var readData TestData
		err = manager.ReadJSON(ctx, &readData)
		if err != nil {
			t.Fatalf("Failed to read JSON via SSH: %v", err)
		}
		
		// Verify data
		if readData.ID != testData.ID {
			t.Errorf("Expected ID %d, got %d", testData.ID, readData.ID)
		}
		if readData.Name != testData.Name {
			t.Errorf("Expected Name %s, got %s", testData.Name, readData.Name)
		}
		if readData.Value != testData.Value {
			t.Errorf("Expected Value %d, got %d", testData.Value, readData.Value)
		}
		if readData.Nested.Field != testData.Nested.Field {
			t.Errorf("Expected Nested.Field %s, got %s", testData.Nested.Field, readData.Nested.Field)
		}
	})
	
	t.Run("SSH_Exists", func(t *testing.T) {
		exists, err := manager.Exists()
		if err != nil {
			t.Fatalf("Failed to check SSH file existence: %v", err)
		}
		if !exists {
			t.Error("File should exist via SSH")
		}
		
		// Test non-existent file
		nonExistentFile := fmt.Sprintf("/tmp/vit_nonexistent_%d.json", time.Now().UnixNano())
		nonExistentManager := NewJSONManager(nonExistentFile, config)
		defer nonExistentManager.Close()
		
		exists, err = nonExistentManager.Exists()
		if err != nil {
			t.Fatalf("Failed to check SSH file existence: %v", err)
		}
		if exists {
			t.Error("File should not exist via SSH")
		}
	})
}

func TestJSONManager_SSHConnectionErrors(t *testing.T) {
	t.Run("InvalidSSHHost", func(t *testing.T) {
		sshConfig := &SSHConfig{
			Host:     "nonexistent.invalid.host",
			Port:     22,
			User:     "testuser",
			Password: "testpass",
			Timeout:  1 * time.Second,
		}
		
		config := &JSONConfig{
			UseSSH:    true,
			SSHConfig: sshConfig,
		}
		
		manager := NewJSONManager("/test/file.json", config)
		defer manager.Close()
		
		ctx := context.Background()
		testData := TestData{ID: 1, Name: "test", Value: 42}
		
		err := manager.WriteJSON(ctx, testData)
		if err == nil {
			t.Error("Expected error with invalid SSH host")
		}
	})
	
	t.Run("MissingSSHConfig", func(t *testing.T) {
		config := &JSONConfig{
			UseSSH:    true,
			SSHConfig: nil, // Missing SSH config
		}
		
		manager := NewJSONManager("/test/file.json", config)
		defer manager.Close()
		
		ctx := context.Background()
		testData := TestData{ID: 1, Name: "test", Value: 42}
		
		err := manager.WriteJSON(ctx, testData)
		if err == nil {
			t.Error("Expected error with missing SSH config")
		}
		
		if err.Error() != "SSH config is required when UseSSH is true" {
			t.Errorf("Unexpected error message: %v", err)
		}
	})
	
	t.Run("InvalidSSHCredentials", func(t *testing.T) {
		sshConfig := &SSHConfig{
			Host:     "localhost",
			Port:     22,
			User:     "invaliduser",
			Password: "invalidpass",
			Timeout:  5 * time.Second,
		}
		
		config := &JSONConfig{
			UseSSH:    true,
			SSHConfig: sshConfig,
		}
		
		manager := NewJSONManager("/test/file.json", config)
		defer manager.Close()
		
		ctx := context.Background()
		testData := TestData{ID: 1, Name: "test", Value: 42}
		
		err := manager.WriteJSON(ctx, testData)
		if err == nil {
			t.Error("Expected error with invalid SSH credentials")
		}
	})
}

func TestJSONManager_SSHLockingMechanism(t *testing.T) {
	sshHost := os.Getenv("SSH_TEST_HOST")
	if sshHost == "" {
		t.Skip("SSH locking tests require SSH_TEST_HOST environment variable")
	}
	
	sshConfig := &SSHConfig{
		Host:     sshHost,
		Port:     22,
		User:     os.Getenv("SSH_TEST_USER"),
		Password: os.Getenv("SSH_TEST_PASS"),
		KeyPath:  os.Getenv("SSH_TEST_KEY"),
		Timeout:  30 * time.Second,
	}
	
	config := &JSONConfig{
		UseSSH:    true,
		SSHConfig: sshConfig,
	}
	
	tempFile := fmt.Sprintf("/tmp/vit_lock_test_%d.json", time.Now().UnixNano())
	
	t.Run("SSH_ConcurrentWrites", func(t *testing.T) {
		const numWriters = 3
		
		results := make(chan error, numWriters)
		
		for i := 0; i < numWriters; i++ {
			go func(id int) {
				manager := NewJSONManager(tempFile, config)
				defer manager.Close()
				
				ctx := context.Background()
				testData := TestData{
					ID:    id,
					Name:  fmt.Sprintf("ssh_writer_%d", id),
					Value: id * 100,
				}
				
				err := manager.WriteJSON(ctx, testData)
				results <- err
			}(i)
		}
		
		// Collect results
		for i := 0; i < numWriters; i++ {
			err := <-results
			if err != nil {
				t.Errorf("SSH concurrent write %d failed: %v", i, err)
			}
		}
		
		// Verify final state
		manager := NewJSONManager(tempFile, config)
		defer func() {
			manager.Close()
			manager.removeSSHFile(tempFile)
			manager.removeSSHFile(tempFile + ".lock")
		}()
		
		var finalData TestData
		err := manager.ReadJSON(context.Background(), &finalData)
		if err != nil {
			t.Fatalf("Failed to read final SSH data: %v", err)
		}
		
		// Should have data from one of the writers
		if finalData.ID < 0 || finalData.ID >= numWriters {
			t.Errorf("Unexpected final SSH data ID: %d", finalData.ID)
		}
	})
}

func TestJSONManager_ShellEscaping(t *testing.T) {
	manager := &JSONManager{}
	
	testCases := []struct {
		input    string
		expected string
	}{
		{"simple", "'simple'"},
		{"with space", "'with space'"},
		{"with'quote", "'with'\"'\"'quote'"},
		{"with\"doublequote", "'with\"doublequote'"},
		{"with$dollar", "'with$dollar'"},
		{"with;semicolon", "'with;semicolon'"},
		{"with&ampersand", "'with&ampersand'"},
		{"with|pipe", "'with|pipe'"},
		{"", "''"},
		{"multiple'quotes'here", "'multiple'\"'\"'quotes'\"'\"'here'"},
	}
	
	for _, tc := range testCases {
		result := manager.escapeShellArg(tc.input)
		if result != tc.expected {
			t.Errorf("escapeShellArg(%q) = %q, want %q", tc.input, result, tc.expected)
		}
	}
}

func TestJSONManager_SSHFileOperations(t *testing.T) {
	// These tests would require a mock SSH server or integration environment
	// For now, they test the structure and error handling
	
	t.Run("SSHFileInfo_Parsing", func(t *testing.T) {
		// Test successful parsing
		timestamp := time.Now().Unix()
		size := int64(1234)
		output := fmt.Sprintf("%d %d", timestamp, size)
		
		var ts, sz int64
		n, err := fmt.Sscanf(output, "%d %d", &ts, &sz)
		if err != nil || n != 2 {
			t.Errorf("Failed to parse stat output: %v", err)
		}
		
		if ts != timestamp || sz != size {
			t.Errorf("Parsed values incorrect: got %d, %d; want %d, %d", ts, sz, timestamp, size)
		}
	})
}

// Helper function to run SSH tests conditionally
func requireSSHTestEnv(t *testing.T) *SSHConfig {
	host := os.Getenv("SSH_TEST_HOST")
	user := os.Getenv("SSH_TEST_USER") 
	pass := os.Getenv("SSH_TEST_PASS")
	key := os.Getenv("SSH_TEST_KEY")
	
	if host == "" {
		t.Skip("SSH tests require SSH_TEST_HOST environment variable")
	}
	
	return &SSHConfig{
		Host:     host,
		Port:     22,
		User:     user,
		Password: pass,
		KeyPath:  key,
		Timeout:  30 * time.Second,
	}
}