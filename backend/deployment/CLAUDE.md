This directory contains the deployment configuration for the Pilates backend, 
which runs on a Kubernetes cluster hosted on AWS.

# Container
- All backend containers share a single image, which can be run using different entrypoints defined in `./entrypoint.sh`
- The entrypoint script accepts a single command argument that determines what process to start:
- `api` - starts the FastAPI server via `uvicorn`

# Kubernetes
Kubernetes configuration is generated and managed by Helm.
The Helm chart lives at `./helm/application/`.

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

Configuration is split across three values files:
- `values.yaml` - common values for all installations (auto-loaded by Helm)
- `values-local.yaml` - overrides for local development (uses a locally built image with `pullPolicy: Never`)
- `values-prod.yaml` - production values (ECR image, HPA, PDB, HTTPRoute, topology constraints)

## Useful Makefile commands

Common `helm` commands are pre-written in `../Makefile`:
- `helm_render` - render templates locally using `values.yaml` and `values-local.yaml`
- `helm_install` - install the chart to a local minikube cluster
- `helm_upgrade` - upgrade (or install) the chart on minikube
- `helm_test` - run the helm-unittest test suite

## Helm tests

Tests are implemented using the `helm-unittest` plugin and live in `./helm/application/tests/`. Run them with:
```
make helm_test
```

To regenerate snapshots after intentional template changes:
```
helm unittest --update-snapshot ./deployment/helm/application/
```
