output "cluster_name" {
  description = "Name of the EKS cluster."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "URL of the EKS cluster API server."
  value       = module.eks.cluster_endpoint
}
