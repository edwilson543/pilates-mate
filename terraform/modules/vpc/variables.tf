variable "name" {
  type        = string
  description = "Name prefix applied to all VPC resources."
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC."
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability zones to deploy public subnets into. Must have the same length as public_subnet_cidrs."
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for public subnets, one per availability zone listed in availability_zones."
}

variable "cluster_name" {
  type        = string
  description = "Name of the EKS cluster. Used to tag subnets so the AWS Load Balancer Controller can discover them."
}
