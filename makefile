PHONY: start stop restart
PHONY: format-gui-api lint-gui-api format-search-api lint-search-api lint-gui-client lint
PHONY: test-gui-api test-search-api test

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

test-gui-api:
	cd gui-api && uv run pytest .

test-search-api:
	cd search-api && uv run pytest .

test: test-gui-api test-search-api
