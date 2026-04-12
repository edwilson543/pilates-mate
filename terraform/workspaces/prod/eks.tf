module "eks" {
  source = "../../modules/eks"

  cluster_name       = local.cluster_name
  kubernetes_version = "1.32"
  subnet_ids         = toset(module.vpc.public_subnet_ids)
  node_instance_type = "t3.medium"
  node_desired_size  = 2
  node_min_size      = 1
  node_max_size      = 3
}

data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}