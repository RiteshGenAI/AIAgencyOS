variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "ai-agency-os"
}

variable "environment" {
  description = "Deployment environment (prod, staging, dev)"
  type        = string
  default     = "prod"
}

variable "image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "backend_secret_key" {
  description = "JWT secret key for the backend. Generate with: openssl rand -hex 32"
  type        = string
  sensitive   = true
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "agency_os"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "ecs_backend_cpu" {
  description = "Fargate CPU units for backend"
  type        = number
  default     = 512
}

variable "ecs_backend_memory" {
  description = "Fargate memory for backend (MiB)"
  type        = number
  default     = 1024
}

variable "ecs_agents_cpu" {
  description = "Fargate CPU units for agents"
  type        = number
  default     = 512
}

variable "ecs_agents_memory" {
  description = "Fargate memory for agents (MiB)"
  type        = number
  default     = 1024
}

variable "ecs_frontend_cpu" {
  description = "Fargate CPU units for frontend"
  type        = number
  default     = 256
}

variable "ecs_frontend_memory" {
  description = "Fargate memory for frontend (MiB)"
  type        = number
  default     = 512
}

variable "llm_provider" {
  description = "LLM provider for agents service (ollama, openai, anthropic)"
  type        = string
  default     = "ollama"
}

variable "llm_model" {
  description = "LLM model name"
  type        = string
  default     = "llama3.2"
}

variable "llm_base_url" {
  description = "Base URL for the LLM provider (e.g. Ollama endpoint)"
  type        = string
  default     = ""
}

variable "llm_api_key" {
  description = "API key for the LLM provider, if required"
  type        = string
  default     = ""
  sensitive   = true
}

variable "allowed_cidr" {
  description = "CIDR block allowed to access the ALB. Use 0.0.0.0/0 for public access."
  type        = string
  default     = "0.0.0.0/0"
}

variable "alb_certificate_arn" {
  description = "ACM certificate ARN for the ALB HTTPS listener. Leave empty to serve HTTP only (not recommended for production)."
  type        = string
  default     = ""
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection on the ALB and RDS"
  type        = bool
  default     = false
}
