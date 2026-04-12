variable "cluster_name" {
  type        = string
  description = "Name of the EKS cluster."
}

variable "kubernetes_version" {
  type        = string
  description = "Kubernetes version for the EKS cluster (e.g. \"1.32\")."
}

variable "subnet_ids" {
  type        = set(string)
  description = "IDs of the subnets the cluster control plane and node group are placed in."
}

variable "node_instance_type" {
  type        = string
  description = "EC2 instance type for the managed node group."
}

variable "node_desired_size" {
  type        = number
  description = "Desired number of nodes in the managed node group."
}

variable "node_min_size" {
  type        = number
  description = "Minimum number of nodes in the managed node group."
}

variable "node_max_size" {
  type        = number
  description = "Maximum number of nodes in the managed node group."
}
