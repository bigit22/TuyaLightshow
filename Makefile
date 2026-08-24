.PHONY: install run dev lint lint-fix startup-enable startup-disable gui build clean

VENV = venv
PYTHON = $(VENV)/Scripts/python.exe
PIP = $(VENV)/Scripts/pip.exe

install:
	python -m venv $(VENV)
	$(PYTHON) -m pip install -U pip
	$(PIP) install -e .

dev: install
	$(PIP) install -e ".[dev]"
	$(VENV)/Scripts/pre-commit install
	$(VENV)/Scripts/pre-commit install --hook-type commit-msg

run:
	$(PYTHON) -m tuyalight run

gui:
	$(PYTHON) -m tuyalight gui

build: dev
	$(PYTHON) -m PyInstaller --noconfirm TuyaLightshow.spec

startup-enable:
	$(PYTHON) -m tuyalight startup --enable

startup-disable:
	$(PYTHON) -m tuyalight startup --disable

lint:
	$(PYTHON) -m ruff check src/
	$(PYTHON) -m mypy src/

lint-fix:
	$(PYTHON) -m ruff check --fix src/
	$(PYTHON) -m ruff format src/

clean:
	ifeq ($(OS),Windows_NT)
		if exist venv rmdir /s /q venv
		if exist .mypy_cache rmdir /s /q .mypy_cache
		if exist .pytest_cache rmdir /s /q .pytest_cache
		if exist dist rmdir /s /q dist
		if exist build rmdir /s /q build
	else
		rm -rf venv .mypy_cache .pytest_cache dist build
	endif
