SHELL = /bin/bash

.DEFAULT_GOAL := help

# Find all python files that are not inside a hidden directory (directory starting with .)
PYTHON_FILES := $(shell find ./* -type f -name "*.py" -print)

# PIPENV files
PIP_FILE = Pipfile
PIP_FILE_LOCK = Pipfile.lock

# Commands
PIPENV_RUN := pipenv run
PYTHON := $(PIPENV_RUN) python3
PIP := $(PIPENV_RUN) pip3
YAPF := $(PIPENV_RUN) yapf
ISORT := $(PIPENV_RUN) isort
PYLINT := $(PIPENV_RUN) pylint



all: help


.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo -e " \033[1mSetup TARGETS\033[0m "
	@echo "- setup              Create the python virtual environment with developper tools and activate it"
	@echo -e " \033[1mFORMATING, LINTING AND TESTING TOOLS TARGETS\033[0m "
	@echo "- format             Format the python source code"
	@echo "- lint               Lint the python source code"
	@echo -e " \033[1mCLEANING TARGETS\033[0m "
	@echo "- clean              Clean python venv"


.PHONY: setup
setup: $(REQUIREMENTS)
	pipenv install --dev
	pipenv shell


# linting target, calls upon yapf to make sure your code is easier to read and respects some conventions.

.PHONY: format
format:
	$(YAPF) -p -i --style .style.yapf $(PYTHON_FILES)
	$(ISORT) $(PYTHON_FILES)


.PHONY: lint
lint:
	$(PYLINT) $(PYTHON_FILES)


 # Clean target

.PHONY: clean
clean_venv:
	pipenv --rm
