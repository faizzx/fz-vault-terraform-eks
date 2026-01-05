terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.14" # Latest stable Helm provider
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # BACKEND: Storing the state in S3 bucket
  backend "s3" {
    bucket         = "fz-vault-tf-state-30eddec3"
    key            = "dev/eks-vault/terraform.tfstate"
    region         = "eu-west-1"
    dynamodb_table = "fz-vault-tf-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  
  # Best Practice: Tag all resources automatically
  default_tags {
    tags = {
      Project     = "fz-vault"
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}