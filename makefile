PHONY: start stop lint-gui-api lint

start:
	docker compose up --build

stop:
	docker-compose down --volumes

restart: stop start

format-gui-api:
	cd gui-api && uv run ruff check --fix . && uv run ruff format

lint-gui-api: format-gui-api
	cd gui-api && uv run ruff check .
	cd gui-api && uv run ty check

format-search-api:
	cd search-api && uv run ruff check --fix . && uv run ruff format

lint-search-api: format-search-api
	cd search-api && uv run ruff check .
	cd search-api && uv run ty check

lint-gui-client:
	cd gui-client && bun run markuplint **/*.html
	cd gui-client && bun run stylelint **/*.css
	cd gui-client && bun run eslint src/**/*.js

lint: lint-gui-api lint-gui-client lint-search-api
