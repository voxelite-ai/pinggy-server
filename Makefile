.PHONY: up down restart

.PHONY: up
up:
	docker build -t pinggy . && \
	docker run -d --name pinggy -p 8000:8080 -v ./.db:/app/db -e DATABASE_URL=/app/db/pinggy.db pinggy

down:
	docker stop pinggy && docker rm pinggy

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

test:
	pytest tests

clean:
	rm -rf db

restart: down up