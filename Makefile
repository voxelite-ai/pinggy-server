.PHONY: up down restart

.PHONY: up
up:
	docker compose -f docker-compose.local.yml down && \
	docker compose -f docker-compose.local.yml up -d --build

down:
	docker compose -f docker-compose.local.yml down

restart: down up