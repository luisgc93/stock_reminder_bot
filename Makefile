install-requirements: ## Install project requirements
	docker-compose exec web pip install -r requirements.txt

env-start: ## Start project containers defined in docker-compose
	docker-compose up -d

env-stop: ## Stop project containers defined in docker-compose
	docker-compose stop

env-destroy: ## Destroy all project containers
	docker-compose down -v --rmi local --remove-orphans

migrate: ## Create mentions table
	docker-compose exec -T worker python -m src.models

env-recreate: env-destroy env-start install-requirements migrate ## Destroy project containers, start them again and run migrations

linting: ## Check/Enforce Python Code-Style
	docker-compose run linting

test: ## Run tests and generate coverage report
	docker-compose run python_test

help: ## Display help text
	@grep '^[a-zA-Z]' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'