APP_NAME = camera_to_web
DOCKER_IMAGE = python:3.11
DOCKER_TAG = latest
WORKDIR = /usr/src/app
ECR_URL = 851725348308.dkr.ecr.us-east-1.amazonaws.com
ECR_REPOSITORY = $(ECR_URL)/$(APP_NAME)
AWS_PROFILE = olhe.ai
AWS_REGION = us-east-1
LIGHTSAIL_SERVICE_NAME = camera-to-web-service
LIGHTSAIL_POWER = small  # Altere conforme necessário (nano, micro, small, medium, large, xlarge)

# Comandos
.PHONY: help build publish run create_env remove_env deploy_dev deploy_prod check clean

help:
	@echo "Comandos disponíveis:"
	@echo "  make build        - Constrói a imagem Docker do projeto"
	@echo "  make publish      - Publica a imagem Docker no ECR"
	@echo "  make run          - Executa a aplicação localmente via Docker"
	@echo "  make create_env   - Cria o serviço de contêiner no AWS Lightsail"
	@echo "  make remove_env   - Remove o serviço de contêiner no AWS Lightsail"
	@echo "  make deploy_dev   - Realiza o deploy no ambiente de desenvolvimento"
	@echo "  make deploy_prod  - Realiza o deploy no ambiente de produção"
	@echo "  make check        - Executa os testes dentro do contêiner Docker"
	@echo "  make clean        - Para, remove e limpa as imagens Docker do projeto"

build:
	@echo "Building the project..."
	docker build -t $(APP_NAME):$(DOCKER_TAG) .

publish:
	@echo "Publishing the Docker image..."
	aws ecr get-login-password --region $(AWS_REGION) --profile $(AWS_PROFILE) | docker login --username AWS --password-stdin $(ECR_URL)
	docker tag $(APP_NAME):$(DOCKER_TAG) $(ECR_REPOSITORY):$(DOCKER_TAG)
	docker push $(ECR_REPOSITORY):$(DOCKER_TAG)

run:
	@echo "Running the application locally via Docker..."
	docker run --name $(APP_NAME) --rm -p 8081:8081 $(APP_NAME):$(DOCKER_TAG)

check:
	@echo "Running tests inside Docker container..."
	docker run --name $(APP_NAME)_test --rm -v $(shell pwd)/fast-api:/app -w /app $(APP_NAME):$(DOCKER_TAG) bash -c "poetry install --no-root --with dev && poetry run pytest -s"

create_env:
	@echo "Creating Lightsail container service..."
	aws lightsail create-container-service --service-name $(LIGHTSAIL_SERVICE_NAME) --power $(LIGHTSAIL_POWER) --scale 1 --region $(AWS_REGION) --profile $(AWS_PROFILE)

remove_env:
	@echo "Removing Lightsail container service..."
	aws lightsail delete-container-service --service-name $(LIGHTSAIL_SERVICE_NAME) --region $(AWS_REGION) --profile $(AWS_PROFILE)

deploy_dev:
	@echo "Running Deploy DEV..."
	aws lightsail update-container-service --service-name $(LIGHTSAIL_SERVICE_NAME) --region $(AWS_REGION) --profile $(AWS_PROFILE) --containers "containerName=$(APP_NAME),image=$(ECR_REPOSITORY):$(DOCKER_TAG),command=[],environment=[],ports={80=HTTP}"

deploy_prod:
	@echo "Running Deploy PROD..."
	# Adicione aqui o comando específico para o deploy de produção se for diferente do deploy_dev

clean:
	@echo "Stopping, removing, and cleaning up Docker images..."
	docker stop $(APP_NAME) || true
	docker rm $(APP_NAME) || true
	docker rmi $(APP_NAME):$(DOCKER_TAG) || true
	docker rmi $(ECR_REPOSITORY):$(DOCKER_TAG) || true
