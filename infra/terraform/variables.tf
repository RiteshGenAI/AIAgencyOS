variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "ai-agency-os"
}

variable "image_tag" {
  description = "Docker image tag"
  type        = string
  default     = "latest"
}
