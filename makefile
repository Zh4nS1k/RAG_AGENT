PYTHON = python3
PIP = pip

.PHONY: help install db-up db-down index run clean

help:
	@echo "Доступные команды:"
	@echo "  make install   - Установить зависимости"
	@echo "  make db-up     - Запустить PostgreSQL в Docker"
	@echo "  make db-down   - Остановить PostgreSQL"
	@echo "  make index     - Запустить индексацию документов"
	@echo "  make run       - Запустить основного агента"
	@echo "  make clean     - Удалить временные файлы"

install:
	$(PIP) install -r requirements.txt

db-up:
	docker run --name postgres-rag -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -e POSTGRES_DB=rag_db -p 5432:5432 -d postgres:latest

db-down:
	docker stop postgres-rag && docker rm postgres-rag

index:
	$(PYTHON) rag_data.py

run:
	$(PYTHON) main.py

clean:
	rm -rf __pycache__
	rm -rf chroma_db_v3
