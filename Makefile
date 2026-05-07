.PHONY: run
run:
	cd backend && make api & cd frontend && make fe

.PHONY: local_ci
local_ci:
	cd backend && make local_ci & cd frontend && make local_ci

.PHONY: format
format:
	cd backend && make format & cd frontend && make format


# Commands for running GitHub actions locally.
actions_args=pull_request --env GITHUB_REF=refs/heads/definitely-not-main --container-architecture=linux/arm64

.PHONY:ci
ci:
	act $(actions_args)

.PHONY:ci-be
ci-be:
	act $(actions_args) --job=backend

.PHONY:ci-fe
ci-fe:
	act $(actions_args) --job=frontend

# Deployment.
.PHONY: deploy
deploy:
	cd backend && make deploy & cd frontend && make deploy
