.PHONY: up down restart

#up: down
#	docker compose -f docker-compose.local.yml up --build -d

.PHONY: up
up:
	docker compose -f docker-compose.local.yml down && \
	docker compose -f docker-compose.local.yml up -d --build

down:
	docker compose -f docker-compose.local.yml down

restart: down up