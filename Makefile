# Makefile for Inity - Cross-platform Python project setup tool
# Developed by Aathish at Strucureo

.PHONY: help install dev build clean test package

help:
	@echo "Inity Build System - Developed by Aathish at Strucureo"
	@echo "Available commands:"
	@echo "  install    - Install Inity for development"
	@echo "  dev        - Set up development environment"
	@echo "  build      - Build executable for current platform"
	@echo "  clean      - Clean build artifacts"
	@echo "  test       - Run tests"
	@echo "  package    - Create distribution package"

install:
	pip install -e .

dev:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .

build:
	python build.py

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

test:
	python -m pytest tests/ -v

package:
	python setup.py sdist bdist_wheel
	
windows:
	python build.py

macos:
	python build.py

linux:
	python build.py
