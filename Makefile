VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

.PHONY: engine venv install clean
URL = https://stockfishchess.org/download/

all: help

venv:
	python3 -m venv $(VENV_DIR)

engine:
	python3 -m scrapper


install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m main

curl:
	curl $(URL)

clean:
	rm -rf $(VENV_DIR)

save_pip:
	python3 -m pip freeze > requirements.txt

help:
	@echo "Comandos disponíveis:"
	@echo "  make venv      -> cria o ambiente virtual"
	@echo "  make install   -> instala dependências"
	@echo "  make run       -> executa o app"
	@echo "  make curl      -> faz requisição HTTP com curl"
	@echo "  make clean     -> remove a venv"
