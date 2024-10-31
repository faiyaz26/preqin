# Variables
VENV_NAME=venv
PYTHON=$(VENV_NAME)/bin/python
PIP=$(VENV_NAME)/bin/pip
BACKEND_DIR=backend
REQUIREMENTS=$(BACKEND_DIR)/requirements.txt

# Colors for terminal output
GREEN=\033[0;32m
NC=\033[0m # No Color

.PHONY: all venv install clean run test

# Default target
all: venv install

# Create virtual environment
venv:
	@echo "$(GREEN)Creating virtual environment...$(NC)"
	python3 -m venv $(VENV_NAME)

# Install dependencies
install: venv
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)

dev-run:
	@echo "$(GREEN)Starting FastAPI development server...$(NC)"
	(PYTHON) -m fastapi dev main:app

# Run tests
test:
	@echo "$(GREEN)Running tests...$(NC)"
	$(PYTHON) -m pytest $(BACKEND_DIR)/tests/

# Clean up generated files and virtual environment
clean:
	@echo "$(GREEN)Cleaning up...$(NC)"
	rm -rf $(VENV_NAME)
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

# Create initial requirements.txt
freeze:
	@echo "$(GREEN)Creating requirements.txt...$(NC)"
	$(PIP) freeze > $(REQUIREMENTS)

# Install development dependencies
dev-install: install
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install black pytest flake8 mypy

# Format code using black
format:
	@echo "$(GREEN)Formatting code...$(NC)"
	$(PYTHON) -m black $(BACKEND_DIR)

# Run linting
lint:
	@echo "$(GREEN)Running linter...$(NC)"
	$(PYTHON) -m flake8 $(BACKEND_DIR)

# Help command
help:
	@echo "Available commands:"
	@echo "  make          : Create venv and install dependencies"
	@echo "  make venv     : Create virtual environment"
	@echo "  make install  : Install dependencies"
	@echo "  make run      : Run the FastAPI server"
	@echo "  make test     : Run tests"
	@echo "  make clean    : Clean up generated files and venv"
	@echo "  make freeze   : Update requirements.txt"
	@echo "  make dev-install : Install development dependencies"
	@echo "  make format   : Format code using black"
	@echo "  make lint     : Run linting"