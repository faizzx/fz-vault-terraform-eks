provider "aws" {
  region = "eu-west-1"
}

# Generates a random string to make the bucket name unique globally
resource "random_id" "suffix" {
  byte_length = 4
}

# 1. The S3 Bucket (The Vault for your Terraform State)
resource "aws_s3_bucket" "state" {
  bucket = "fz-vault-tf-state-${random_id.suffix.hex}"
  
  lifecycle {
    prevent_destroy = true
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# 2. The DynamoDB Table (The Locking Mechanism)
resource "aws_dynamodb_table" "locks" {
  name         = "fz-vault-tf-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

output "state_bucket_name" {
  value = aws_s3_bucket.state.bucket
}
