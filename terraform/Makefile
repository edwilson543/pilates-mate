.PHONY: fmt lint init-prod plan-prod apply-prod destroy-prod

fmt:
	tofu fmt -recursive

lint:
	tofu fmt -recursive -check
	tflint --recursive

init-prod:
	tofu -chdir=workspaces/prod init

plan-prod: init-prod
	tofu -chdir=workspaces/prod plan

apply-prod: init-prod
	tofu -chdir=workspaces/prod apply

destroy-prod: init-prod
	tofu -chdir=workspaces/prod destroy
