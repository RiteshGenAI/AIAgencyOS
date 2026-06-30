output "alb_dns_name" {
  description = "Application Load Balancer DNS name. Point your domain or browser here."
  value       = aws_lb.main.dns_name
}

output "alb_zone_id" {
  description = "Route 53 hosted zone ID for the ALB"
  value       = aws_lb.main.zone_id
}

output "ecr_backend_repository_url" {
  description = "ECR repository URL for backend images"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_agents_repository_url" {
  description = "ECR repository URL for agents images"
  value       = aws_ecr_repository.agents.repository_url
}

output "ecr_frontend_repository_url" {
  description = "ECR repository URL for frontend images"
  value       = aws_ecr_repository.frontend.repository_url
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.address
}

output "db_secret_arn" {
  description = "ARN of the Secrets Manager secret containing the database URL"
  value       = aws_secretsmanager_secret.db_url.arn
  sensitive   = true
}

output "backend_secret_key_arn" {
  description = "ARN of the Secrets Manager secret containing the backend JWT secret key"
  value       = aws_secretsmanager_secret.backend_secret_key.arn
  sensitive   = true
}

output "s3_artifacts_bucket" {
  description = "S3 bucket for build artifacts and backups"
  value       = aws_s3_bucket.artifacts.id
}
