PYTHON ?= $(shell command -v python3.13 2>/dev/null || command -v python3.12 2>/dev/null || command -v python3.11 2>/dev/null || command -v python3)
VENV := .venv
BIN := $(VENV)/bin
APP_PORT ?= 8080

.PHONY: help venv install qdrant-up qdrant-down qdrant-logs ingest run dev health chat clean

help:
	@echo "Available targets:"
	@echo "  make install      Create virtualenv and install dependencies"
	@echo "                    Override Python with: make install PYTHON=python3.12"
	@echo "  make qdrant-up    Start Qdrant with Docker Compose"
	@echo "  make ingest       Ingest documents from data/docs into Qdrant"
	@echo "  make run          Run the FastAPI server"
	@echo "  make health       Call GET /health"
	@echo "  make chat         Send a sample chat request"
	@echo "  make qdrant-down  Stop Qdrant"
	@echo "  make clean        Remove Python cache files"

venv:
	@echo "Using Python: $(PYTHON)"
	$(PYTHON) -m venv $(VENV)

install: venv
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

qdrant-up:
	docker compose up -d qdrant

qdrant-down:
	docker compose down

qdrant-logs:
	docker compose logs -f qdrant

ingest:
	$(BIN)/python -m rag_chatbot.ingest --data-dir data/docs

run:
	$(BIN)/uvicorn rag_chatbot.api:app --host 0.0.0.0 --port $(APP_PORT)

dev:
	$(BIN)/uvicorn rag_chatbot.api:app --host 0.0.0.0 --port $(APP_PORT) --reload

health:
	curl http://localhost:$(APP_PORT)/health

chat:
	curl -X POST http://localhost:$(APP_PORT)/chat \
		-H "Content-Type: application/json" \
		-d '{"message":"What is this document about?"}'

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
