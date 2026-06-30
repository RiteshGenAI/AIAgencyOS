resource "aws_ecr_repository" "backend" {
  name = "${var.project_name}-backend"
}

resource "aws_ecr_repository" "agents" {
  name = "${var.project_name}-agents"
}

resource "aws_ecr_repository" "frontend" {
  name = "${var.project_name}-frontend"
}
