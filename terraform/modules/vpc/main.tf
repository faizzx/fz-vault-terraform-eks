data "aws_availability_zones" "available" {}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = var.vpc_name
  cidr = var.vpc_cidr

  # Dynamically pick the first two AZs in the region (e.g., eu-west-1a, eu-west-1b)
  azs = slice(data.aws_availability_zones.available.names, 0, 2)

  # Private Subnets: Where your EKS Nodes (EC2) & Database (RDS) live
  # Not accessible from the internet directly.
  private_subnets = [
    cidrsubnet(var.vpc_cidr, 8, 1), # 10.0.1.0/24
    cidrsubnet(var.vpc_cidr, 8, 2)  # 10.0.2.0/24
  ]

  # Public Subnets: Where the Load Balancer lives
  public_subnets = [
    cidrsubnet(var.vpc_cidr, 8, 101), # 10.0.101.0/24
    cidrsubnet(var.vpc_cidr, 8, 102)  # 10.0.102.0/24
  ]

  # NAT Gateway: Allows private nodes to download updates from the internet securely
  enable_nat_gateway = true
  single_nat_gateway = true # Cost saving for dev (Production usually has one per AZ)

  # DNS Hostnames: Required for EKS to function
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Tags required by Kubernetes to discover subnets for Load Balancers
  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
  }
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}