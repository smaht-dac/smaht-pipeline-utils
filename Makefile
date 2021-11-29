configure:
	pip install poetry

build:
	poetry install

info:
	@: $(info Here are some 'make' options:)
	   $(info - Use 'make configure' to configure the repo by installing poetry.)
	   $(info - Use 'make build' to install entry point commands.)
