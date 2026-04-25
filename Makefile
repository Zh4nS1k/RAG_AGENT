.PHONY: install run-backend run-frontend db-up db-down index

install:
	cd rag_agent_001 && $(MAKE) install

db-up:
	cd rag_agent_001 && $(MAKE) db-up

db-down:
	cd rag_agent_001 && $(MAKE) db-down

index:
	cd rag_agent_001 && $(MAKE) index

run-backend:
	cd rag_agent_001 && $(MAKE) run-backend

run-frontend:
	cd rag_agent_001 && $(MAKE) run-frontend

help:
	@echo "Доступные команды:"
	@echo "  make install       - Установить зависимости бэкенда и фронтенда"
	@echo "  make db-up         - Запустить PostgreSQL в Docker"
	@echo "  make db-down       - Остановить PostgreSQL"
	@echo "  make index         - Запустить индексацию документов"
	@echo "  make run-backend   - Запустить FastAPI сервер"
	@echo "  make run-frontend  - Запустить Next.js сервер"
