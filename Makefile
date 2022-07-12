help:
	@echo "available commands are:"
	@echo "	- run : launch app"
	@echo "	- clean: del pycache and pyc."
	@echo "	- test: launch tests"
	@echo "	- init: install required packages"

run:
	python3 vit

clean:
	rm -rf __pycache__
	rm -rf *.pyc

test:
	python3 -m unittest discover tests

init: requirements.txt
	pip3 install -r requirements.txt

#install:
#	don't know yet.

# distinstall: 
#	don't know yet.