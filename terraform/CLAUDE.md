The application is deployed on AWS infrastructure and managed by Terraform (executed via OpenTofu).
This directory contains the Terraform code.

# Terraform structure

The Terraform code is organised into:
- `modules/` — re-usable modules, each focused on a single AWS component:
  - `modules/vpc/` — VPC with public subnets, internet gateway, and route tables
  - `modules/eks/` — EKS cluster, managed node group, IAM roles, and OIDC provider
- `workspaces/` — deployment environments; each workspace has its own state:
  - `workspaces/prod/` — production environment (eu-west-2)

# AWS services used

| Service | Purpose |
|---|---|
| Amazon EKS | Managed Kubernetes cluster hosting the backend pods |
| Amazon VPC | Network isolation; public subnets only (no NAT gateway) |
| AWS ALB | Internet-facing load balancer, provisioned by the AWS Load Balancer Controller via the `Gateway` resource |
| AWS IAM | Roles and OIDC provider for IRSA (pod-level AWS permissions) |
| Amazon ECR | Container image registry (pre-existing, not managed here) |

# Conventions

- Use `aws_iam_policy_document` data sources for all IAM trust and permission policies
- Use `locals` in workspaces rather than variable defaults
- Use `for_each` / `set` / `map` rather than `count` / `list` to avoid resource recreation on reordering
- Modules do not specify provider version constraints — these are managed at the workspace level

# Apply pipeline

Commands are run from `./terraform/` using `make`:

```bash
make fmt          # Format all .tf files with tofu fmt
make lint         # Run tflint across all modules and workspaces
make init-prod    # Initialise the prod workspace (download providers)
make plan-prod    # Preview changes to the prod environment
make apply-prod   # Apply changes to the prod environment
make destroy-prod # Destroy all prod resources
```

Prerequisites:
- AWS credentials configured (e.g. via `~/.aws/credentials` or environment variables)
- `tofu` CLI installed
- `tflint` installed with the AWS plugin (`tflint --init` from the terraform root)

# Deploying the application

Terraform provisions the cluster infrastructure only. To deploy the backend application after
`make apply-prod`:

1. Authenticate with ECR: `aws ecr get-login-password --region eu-west-2 | docker login ...`
2. Build and push the image to ECR
3. Update kubeconfig: `aws eks update-kubeconfig --region eu-west-2 --name pilates`
4. Deploy the helm chart: `helm upgrade --install pilates ./backend/deployment/helm/application -n pilates`
