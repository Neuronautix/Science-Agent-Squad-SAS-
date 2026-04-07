.PHONY: setup run ingest info scaffold test clean help

# PIU Psych Swarm — Makefile

VENV     = .venv

ifeq ($(OS),Windows_NT)
PYTHON_BOOTSTRAP ?= py -3
PYTHON   = $(VENV)/Scripts/python.exe
PIP      = $(VENV)/Scripts/pip.exe
ACTIVATE = $(VENV)/Scripts/activate
BLANK_LINE_CMD = echo.
ENV_COPY_CMD = if not exist .env (copy .env.example .env & echo .env created from .env.example) else (echo .env already exists)
REMOVE_VENV_CMD = if exist $(VENV) rmdir /s /q $(VENV)
REMOVE_AUTOMATION_CACHE_CMD = if exist automation\__pycache__ rmdir /s /q automation\__pycache__
REMOVE_ROOT_CACHE_CMD = if exist __pycache__ rmdir /s /q __pycache__
REMOVE_DB_CMD = if exist automation\db rmdir /s /q automation\db
else
PYTHON_BOOTSTRAP ?= python3
PYTHON   = $(VENV)/bin/python
PIP      = $(VENV)/bin/pip
ACTIVATE = $(VENV)/bin/activate
BLANK_LINE_CMD = printf '\n'
ENV_COPY_CMD = if [ ! -f .env ]; then cp .env.example .env; echo .env created from .env.example; else echo .env already exists; fi
REMOVE_VENV_CMD = rm -rf $(VENV)
REMOVE_AUTOMATION_CACHE_CMD = rm -rf automation/__pycache__
REMOVE_ROOT_CACHE_CMD = rm -rf __pycache__
REMOVE_DB_CMD = rm -rf automation/db
endif

help:
	@$(BLANK_LINE_CMD)
	@echo   PIU Psych Swarm — Available Commands
	@echo   ====================================
	@echo   make setup       Create venv, install deps, copy .env.example
	@echo   make run         Run the swarm (set PROMPT="your prompt")
	@echo   make ingest      Vectorize documents from active agents/*/KB/ folders
	@echo   make info        Display the current swarm configuration
	@echo   make scaffold    Scaffold a new domain (set DOMAIN="your domain")
	@echo   make test        Run the test suite
	@echo   make clean       Remove venv and cached files
	@$(BLANK_LINE_CMD)

setup:
	@echo Creating virtual environment...
	$(PYTHON_BOOTSTRAP) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@$(ENV_COPY_CMD)
	@$(BLANK_LINE_CMD)
	@echo Setup complete.
	@echo    1. Edit .env with your API keys
	@echo    2. Run: make info
	@echo    3. Run: make run PROMPT="Review problematic internet use in adolescents"

run:
ifndef PROMPT
	@echo ERROR: Please provide a prompt.
	@echo Usage: make run PROMPT="Review the psychiatric literature on problematic internet use"
	@exit /b 1
endif
	$(PYTHON) -m automation.main execute "$(PROMPT)"

ingest:
	@echo Vectorizing Knowledge Base documents...
	$(PYTHON) -m automation.ingest

info:
	$(PYTHON) -m automation.main info

scaffold:
ifndef DOMAIN
	@echo ERROR: Please provide a domain name.
	@echo Usage: make scaffold DOMAIN="Climate Science"
	@exit /b 1
endif
	$(PYTHON) -m automation.main scaffold "$(DOMAIN)"

test:
	$(PYTHON) -m pytest tests/ -v

clean:
	@echo Cleaning up...
	@$(REMOVE_VENV_CMD)
	@$(REMOVE_AUTOMATION_CACHE_CMD)
	@$(REMOVE_ROOT_CACHE_CMD)
	@$(REMOVE_DB_CMD)
	@echo Cleaned.
