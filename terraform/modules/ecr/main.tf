resource "aws_ecr_repository" "app_repo" {
  name                 = var.repo_name
  image_tag_mutability = "MUTABLE" # Allows overwriting tags like 'latest'

  # Security: Scan images for vulnerabilities (CVEs) automatically on push
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = "dev"
    Project     = "fz-vault"
  }
}

# Lifecycle Policy: Automatically clean up old images to save money
resource "aws_ecr_lifecycle_policy" "cleanup" {
  repository = aws_ecr_repository.app_repo.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only the last 5 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 3
      }
      action = {
        type = "expire"
      }
    }]
  })
}

# Output the URL so we can push to it later
output "repository_url" {
  value = aws_ecr_repository.app_repo.repository_url
}