This directory contains the deployment configuration for the Pilates backend, 
which runs on a Kubernetes cluster hosted on AWS.

# Container
- All backend containers share a single image, which can be run using different entrypoints defined in `./entrypoint.sh`
- The entrypoint script accepts a single command argument that determines what process to start:
- `api` - starts the FastAPI server via `uvicorn`

# Kubernetes
Kubernetes configuration is generated and managed by Helm.
The Helm chart lives at `./k8s/application/`.

## Helm chart

The chart deploys the following resources:
- `api/deployment.yaml` - the API server deployment
- `api/hpa.yaml` - horizontal pod autoscaler for the API (enabled by default)
- `api/pdb.yaml` - pod disruption budget for the API (enabled by default, `minAvailable: 1`)
- `api/configmap.yaml` - non-sensitive environment variables (only rendered when `api.environment` is non-empty)
- `api/secret.yaml` - secret environment variables (only rendered when `api.secrets` is non-empty)
- `service.yaml` - ClusterIP service fronting the API
- `serviceaccount.yaml` - service account for the API pods
- `httproute.yaml` - Gateway API HTTPRoute for external traffic (enabled by default, disabled locally)

Configuration is split across two values files:
- `values.yaml` - production defaults
- `values-local.yaml` - overrides for local development (disables HTTPRoute and PDB, uses a locally built image)

## Useful Makefile commands

Common `helm` commands are pre-written in `../Makefile`:
- `helm_render` - render templates locally using `values-local.yaml`
- `helm_install` - install the chart to a local minikube cluster
- `helm_upgrade` - upgrade (or install) the chart on minikube
- `helm_test` - run the helm-unittest test suite

## Helm tests

Tests are implemented using the `helm-unittest` plugin and live in `./k8s/application/tests/`. Run them with:
```
make helm_test
```

To regenerate snapshots after intentional template changes:
```
helm unittest --update-snapshot ./deployment/k8s/application/
```

# Infrastructure
The application is deployed on AWS infrastructure and managed by Terraform.                                                                                                      

## Terraform structure                                                                                                                                                           
The Terraform code for the backend lives in `./terraform`.                                                                                                                       
At root, the package is organised into:                                                                                                                                          
- Workspaces:                                                                                                                                                                    
  - Each workspace represents an isolated deployment environment                                                                                                                 
  - Each workspace's Terraform state is therefore tracked independently                                                                                                          
  - For example `./terraform/workspaces/prod` contains the production deployment environment                                                                                     
- Modules:                                                                                                                                                                       
  - These contain re-usable collections of Terraform configuration files                                                                                                         
  - For example `./terraform/modules/eks` contains the configuration files for deploying an EKS cluster

TODO: document the AWS services used, Terraform conventions, and the apply pipeline.
