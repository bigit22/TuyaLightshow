.PHONY: install run dev lint startup-enable startup-disable clean

VENV = venv
PYTHON = $(VENV)/Scripts/python.exe
PIP = $(VENV)/Scripts/pip.exe

install:
	python -m venv $(VENV)
	$(PYTHON) -m pip install -U pip
	$(PIP) install -e .


dev: install
	$(PIP) install pre-commit
	$(VENV)/Scripts/pre-commit install
	$(VENV)/Scripts/pre-commit install --hook-type commit-msg

run:
	$(PYTHON) -m tuyalight run

startup-enable:
	$(PYTHON) -m tuyalight startup --enable

startup-disable:
	$(PYTHON) -m tuyalight startup --disable

lint:
	$(PYTHON) -m ruff check src/
	$(PYTHON) -m mypy src/

clean:
	rm -rf $(VENV)
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf *.egg-info
