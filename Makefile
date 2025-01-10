help:
	@echo "available commands are:"

init: 
	@python3 -m pip install --upgrade pip
	@python3 -m pip install --upgrade build
	@python3 -m pip install pipx

venv: 
	@./make_venv.sh

dist: 
	@$(MAKE) clean
	@python3 -m build

distinstall: 
	@$(MAKE) clean
	@python3 -m build 
	@pipx install dist/*.whl --force

clean:
	@if [ -d "venv" ]; then \
		rm -rf "venv"; \
	fi
		
	@if [ -d "dist" ]; then \
		rm -rf "dist"; \
	fi

test:
	@if [ ! -d "venv" ]; then \
		$(MAKE) venv; \
	fi
	@$(shell source venv/bin/activate && python3 -m unittest discover tests && deactivate)

.PHONY: coverage
coverage:
	@if [ ! -d "venv" ]; then \
		$(MAKE) venv; \
	fi
	@if [ ! -f ".coverage" ]; then \
		rm -f ".coverage"; \
	fi
	@$(shell source venv/bin/activate && coverage run -m unittest discover &> /dev/null && deactivate )
	@coverage report

