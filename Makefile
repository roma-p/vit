.PHONY: test build clean

test:
	go test ./... -v

build:
	go build -o vit

clean:
	rm -f vit 
