# Linting.

.PHONY: fmt lint
fmt:
	tofu fmt -recursive

lint:
	tofu fmt -recursive -check
	tflint --recursive


# Deployment.
.PHONY: plan
plan:
	tofu -chdir=workspaces/dev plan


.PHONY: apply
apply:
	tofu -chdir=workspaces/dev apply