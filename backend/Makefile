# Installation.

.PHONY:install
install:
	uv sync --locked
	uv pip install -e .

# Application.

.PHONY:api
api:
	uv run uvicorn pilates.interfaces.api.app:app --port=8000

.PHONY:eval
eval:
	uv run pilates evaluate-prompt

# Static analysis.

local_ci: lint test helm_test

.PHONY:test
test:
	uv run pytest .

lint: check mypy lint_imports

.PHONY:mypy
mypy:
	uv run mypy .

.PHONY:format
format:
	uv run ruff format .
	uv run ruff check . --fix

.PHONY:check
check:
	uv run ruff format . --check
	uv run ruff check .

.PHONY:lint_imports
lint_imports:
	uv run lint-imports

# Docker.

app_version = $(shell bash deployment/version.sh)
docker_tag = $(shell echo $(app_version) | sed 's/+/-/')
ecr_registry = 127624060144.dkr.ecr.eu-west-2.amazonaws.com
ecr_repo = $(ecr_registry)/pilates

docker_server: docker_image docker_run

.PHONY:docker_run
docker_run:
	docker container rm pilates -v || true
	docker container run -p 8000:8000 --name=pilates pilates:latest api

.PHONY:docker_image
docker_image:
	docker image build . -t pilates:latest -t pilates:$(docker_tag) --build-arg="APP_VERSION=$(app_version)"

.PHONY:ecr_login
ecr_login:
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin $(ecr_registry)

.PHONY:ecr_push
ecr_push: docker_image ecr_login
	docker image tag pilates:$(docker_tag) $(ecr_repo):$(docker_tag)
	docker image tag pilates:latest $(ecr_repo):latest
	docker push $(ecr_repo):$(docker_tag)
	docker push $(ecr_repo):latest
	echo 'Pushed Docker image to ECR with tag:' $(docker_tag)

# Helm (local).
.PHONY:helm_render
helm_render:
	helm template application ./deployment/helm/application/ --output-dir ./deployment/helm/rendered -f ./deployment/helm/application/values-local.yaml

.PHONY:helm_install
helm_install:
	helm install application ./deployment/helm/application/ --kube-context minikube --namespace pilates -f ./deployment/helm/application/values-local.yaml

.PHONY:helm_upgrade
helm_upgrade:
	helm upgrade --install application ./deployment/helm/application/ --kube-context minikube --namespace pilates -f ./deployment/helm/application/values-local.yaml

.PHONY:helm_test
helm_test:
	helm unittest ./deployment/helm/application/

.PHONY:helm_list
helm_list:
	helm list -A --kube-context minikube --namespace default

# K8s (local).
.PHONY:k8s_docker_image
k8s_docker_image:
	eval $(minikube docker-env)
	${MAKE} docker_image

.PHONY:k8s_pf
k8s_pf:
	kubectl port-forward service/application-pilates 8000:80 --context=minikube --namespace=pilates

# Deployment.

.PHONY:version
version:
	bash ./deployment/version.sh
