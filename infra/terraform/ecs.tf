# Skeleton ECS resources - to be expanded.

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}
