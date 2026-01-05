# 1. The Network
module "vpc" {
  source = "./modules/vpc"

  vpc_name = "fz-vault-vpc"
  vpc_cidr = "10.0.0.0/16"
}

# 2. The Cluster
module "eks" {
  source = "./modules/eks"
  cluster_name = "fz-vault-cluster"

  # Pass the VPC outputs into the EKS module
  vpc_id     = module.vpc.vpc_id
  
  # Keeping Nodes in PRIVATE subnets for security
  subnet_ids = module.vpc.private_subnets
}

# 3. The ECR registry to upload code/container image
module "ecr" {
  source = "./modules/ecr"

  repo_name = "fz-vault-app"
}