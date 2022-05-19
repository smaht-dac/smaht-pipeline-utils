.PHONY: build

configure:
	pip install --upgrade pip
	pip install poetry

update:
	poetry update

build:
	poetry install

info:
	@: $(info Here are some 'make' options:)
	   $(info - Use 'make configure' to configure the repo by installing poetry.)
	   $(info - Use 'make update' to update dependencies and the lock file.)
	   $(info - Use 'make build' to install entry point commands.)
