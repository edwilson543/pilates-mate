resource "kubernetes_namespace" "pilates" {
  metadata {
    name = "pilates"
  }

  depends_on = [module.eks]
}