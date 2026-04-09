COLOR_GREEN = \033[0;32m
COLOR_BLUE  = \033[0;34m
COLOR_NC    = \033[0m

DOCKER_EXEC = docker-compose -f docker-compose.local.yml exec django

.PHONY: setup run migrations migrate test format superuser shell

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
	$(DOCKER_EXEC) uv run python manage.py test

format:
	@echo "$(COLOR_BLUE)Starting ruff isort (import sorting)$(COLOR_NC)"
	$(DOCKER_EXEC) uv run ruff check --select I --fix .
	@echo "OK\n"

	@echo "$(COLOR_BLUE)Starting ruff format (code formatting)$(COLOR_NC)"
	$(DOCKER_EXEC) uv run ruff format .
	@echo "OK\n"

	@echo "$(COLOR_GREEN)Code Formatting successfully!$(COLOR_NC)"

superuser:
	$(DOCKER_EXEC) uv run python manage.py createsuperuser

shell:
	$(DOCKER_EXEC) uv run python manage.py shell