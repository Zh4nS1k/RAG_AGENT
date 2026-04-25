.PHONY: install run-backend run-frontend db-up db-down index

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

db-up:
	docker run --name postgres-rag -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -e POSTGRES_DB=rag_db -p 5432:5432 -d postgres:latest || docker start postgres-rag

db-down:
	docker stop postgres-rag

index:
	cd backend && python rag_data.py

run-backend:
	cd backend && python main.py

run-frontend:
	cd frontend && npm run dev

all: db-up run-backend
