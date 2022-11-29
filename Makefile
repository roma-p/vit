help:
	@echo "available commands are:"
	@echo "	- run : launch app, use ARGS='<args here>'"
	@echo "	- clean: remove distinstall directories."
	@echo "	- test: launch tests"
	@echo "	- coverage: display current test coverage"
	@echo "	- init: install required packages"
	@echo "	- distinstall: create wheel for dist install."

run:
	PYTHONPATH="." python3 vit $(ARGS)

clean:
	rm -r build
	rm -r dist
	rm -r vit.egg-info

test:
	python3 -m unittest discover tests

coverage:
	coverage run -m unittest discover &> /dev/null ;  coverage report

init: requirements.txt
	pip3 install -r requirements.txt

install:
	python3 setup.py bdist_wheel
	python3 -m pip install dist/*.whl --force-reinstall

distinstall:
	python3 setup.py bdist_wheel
