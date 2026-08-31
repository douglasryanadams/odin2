PHONY: start stop lint-gui-api lint

start:
	docker compose up --build

stop:
	docker-compose down --volumes

dev:
	cd gui-client && bun src/index.html

format-gui-api:
	cd gui-api && uv run ruff check --fix . && uv run ruff format

lint-gui-api: format-gui-api
	cd gui-api && uv run ruff check .
	cd gui-api && uv run ty check

lint-gui-client:
	cd gui-client && bun run markuplint **/*.html
	cd gui-client && bun run stylelint **/*.css

lint: lint-gui-api lint-gui-client
