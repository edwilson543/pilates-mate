# Resources are split across named files:
#   locals.tf        - workspace-level locals (region, cluster name)
#   vpc.tf           - VPC module
#   eks.tf           - EKS cluster module + cluster auth data source
#   namespace.tf     - Kubernetes namespace
#   alb_controller.tf - AWS Load Balancer Controller (IAM + Helm release)
#   gateway.tf       - Gateway API CRDs (Helm release) + Gateway resource
