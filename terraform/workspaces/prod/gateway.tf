# Gateway API CRDs must be installed before the AWS Load Balancer Controller can reconcile
# Gateway and HTTPRoute resources.
resource "helm_release" "gateway_api_crds" {
  name      = "gateway-api"
  chart     = "oci://ghcr.io/kubernetes-sigs/gateway-api/charts/gateway-api"
  version   = "1.2.1"
  namespace = "kube-system"

  depends_on = [module.eks]
}

# The Gateway resource in the pilates namespace. The AWS Load Balancer Controller provisions
# an internet-facing ALB to back this Gateway. The HTTPRoute in the application helm chart
# attaches to this Gateway via parentRefs.name = "gateway".
resource "kubernetes_manifest" "gateway" {
  manifest = {
    apiVersion = "gateway.networking.k8s.io/v1"
    kind       = "Gateway"
    metadata = {
      name      = "gateway"
      namespace = "pilates"
      annotations = {
        "alb.ingress.kubernetes.io/scheme"      = "internet-facing"
        "alb.ingress.kubernetes.io/target-type" = "ip"
      }
    }
    spec = {
      gatewayClassName = "amazon-alb"
      listeners = [
        {
          name     = "http"
          port     = 80
          protocol = "HTTP"
          allowedRoutes = {
            namespaces = {
              from = "Same"
            }
          }
        }
      ]
    }
  }

  depends_on = [
    helm_release.gateway_api_crds,
    helm_release.aws_load_balancer_controller,
    kubernetes_namespace.pilates,
  ]
}
