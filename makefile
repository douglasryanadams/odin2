PHONY: start stop lint-gui-api lint

start:
	docker compose up --build

stop:
	docker-compose down --volumes

format-gui-api:
	cd gui-api && uv run ruff check --fix . && uv run ruff format

lint-gui-api: format-gui-api
	cd gui-api && uv run ruff check .
	cd gui-api && uv run ty check

lint: lint-gui-api
