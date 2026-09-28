VENV_DIR := .venv
PYTHON ?= $(shell for v in python3.10 python3.11 python3.12 python3.13 python3; do if command -v $$v >/dev/null 2>&1; then echo $$v; break; fi; done)
VENV_PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
STOCKFISH_URL := https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-linux-x86-64-universal.tar.gz
ENGINE_DIR := ./data/engine

.DEFAULT_GOAL := help

.PHONY: venv install engine run clean help save_pip

venv:
	@echo "Usando Python: $(PYTHON)"
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "Python compatível não encontrado. Instale python3.10+"; exit 1; }
	$(PYTHON) -m venv $(VENV_DIR)

install: venv
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt

engine: install
	@mkdir -p $(ENGINE_DIR)
	@curl -fL --retry 3 -o /tmp/stockfish.tar.gz "$(STOCKFISH_URL)"
	@rm -rf /tmp/stockfish-extract
	@mkdir -p /tmp/stockfish-extract
	@tar -xzf /tmp/stockfish.tar.gz -C /tmp/stockfish-extract
	@STOCKFISH_BIN=$$(find /tmp/stockfish-extract -type f -executable -name 'stockfish' | head -n 1); \
		if [ -z "$$STOCKFISH_BIN" ]; then \
			echo "Erro: binário do Stockfish não foi encontrado no pacote baixado."; \
			exit 1; \
		fi; \
		cp "$$STOCKFISH_BIN" "$(ENGINE_DIR)/stockfish"; \
		chmod +x "$(ENGINE_DIR)/stockfish"; \
		echo "Stockfish instalado em $(ENGINE_DIR)/stockfish"; \
		ls -l "$(ENGINE_DIR)/stockfish"

run: venv
	$(VENV_PYTHON) -m main

curl:
	curl -I $(STOCKFISH_URL)

clean:
	rm -rf $(VENV_DIR) __pycache__ .pytest_cache $(ENGINE_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

save_pip: venv
	$(VENV_PYTHON) -m pip freeze > requirements.txt

help:
	@echo "Comandos disponíveis:"
	@echo "  make venv       -> cria o ambiente virtual"
	@echo "  make install    -> instala dependências"
	@echo "  make engine     -> baixa e instala o Stockfish em data/engine"
	@echo "  make run        -> executa o app"
	@echo "  make curl       -> testa o link do Stockfish"
	@echo "  make save_pip   -> salva dependências no requirements.txt"
	@echo "  make clean      -> remove a venv e o engine"
