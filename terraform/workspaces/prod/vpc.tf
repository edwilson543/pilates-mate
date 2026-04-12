module "vpc" {
  source = "../../modules/vpc"

  name                = local.cluster_name
  vpc_cidr            = "10.0.0.0/16"
  availability_zones  = ["${local.aws_region}a", "${local.aws_region}b"]
  public_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24"]
  cluster_name        = local.cluster_name
}