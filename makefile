COLOR_GREEN = \033[0;32m
COLOR_BLUE  = \033[0;34m
COLOR_NC    = \033[0m

DOCKER_EXEC = docker compose --env-file envs/.env -f deployments/docker/docker-compose.local.yml exec django

.PHONY: setup run migrations migrate test ruff mypy superuser shell docker_up docker_up_build docker_down docker_down_v seed

setup:
	@echo "$(COLOR_BLUE)Syncing dependencies inside Docker...$(COLOR_NC)"
	$(DOCKER_EXEC) uv sync
	@echo "$(COLOR_GREEN)Setup complete!$(COLOR_NC)\n"

run:
	$(DOCKER_EXEC) uv run python manage.py runserver

migrations:
	$(DOCKER_EXEC) uv run python manage.py makemigrations

migrate:
	$(DOCKER_EXEC) uv run python manage.py migrate

test:
	@echo "$(COLOR_BLUE)Running Django tests inside Docker...$(COLOR_NC)"
	$(DOCKER_EXEC) uv run coverage run manage.py test
	$(DOCKER_EXEC) uv run coverage report -m
	$(DOCKER_EXEC) uv run coverage html

ruff:
	@echo "$(COLOR_BLUE)Starting ruff isort (import sorting)$(COLOR_NC)"
	$(DOCKER_EXEC) uv run ruff check . --fix
	@echo "OK\n"

	@echo "$(COLOR_BLUE)Starting ruff format (code formatting)$(COLOR_NC)"
	$(DOCKER_EXEC) uv run ruff format .
	@echo "OK\n"

	@echo "$(COLOR_GREEN)run ruff successfully!$(COLOR_NC)"

mypy:
	@echo "$(COLOR_BLUE)Starting mypy (type check)$(COLOR_NC)"
	$(DOCKER_EXEC) uv run mypy .
	@echo "OK\n"
	@echo "$(COLOR_GREEN)run mypy successfully!$(COLOR_NC)"

superuser:
	$(DOCKER_EXEC) uv run python manage.py createsuperuser

shell:
	$(DOCKER_EXEC) uv run python manage.py shell

docker_up:
	docker compose --env-file envs/.env -f deployments/docker/docker-compose.local.yml up -d

docker_up_build:
	docker compose --env-file envs/.env -f deployments/docker/docker-compose.local.yml up --build -d

docker_up_build_no-d:
	docker compose --env-file envs/.env -f deployments/docker/docker-compose.local.yml up --build
docker_down:
	docker compose --env-file envs/.env -f deployments/docker/docker-compose.local.yml down

docker_down_v:
	docker compose --env-file envs/.env -f deployments/docker/docker-compose.local.yml down -v

seed:
	@echo "$(COLOR_BLUE)Seeding scent data from S3...$(COLOR_NC)"
	$(DOCKER_EXEC) uv run env PYTHONPATH=/one_piece python scripts/seed_scent.py
	@echo "$(COLOR_GREEN)Seed complete!$(COLOR_NC)\n"