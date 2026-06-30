resource "aws_db_subnet_group" "main" {
  name        = "${local.name_prefix}-db-subnet-group"
  description = "Subnet group for ${local.name_prefix} RDS"
  subnet_ids  = aws_subnet.private[*].id

  tags = {
    Name = "${local.name_prefix}-db-subnet-group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier             = "${local.name_prefix}-postgres"
  engine                 = "postgres"
  engine_version         = "16.1"
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  max_allocated_storage  = 100
  storage_type           = "gp3"
  storage_encrypted      = true
  db_name                = "agency_os"
  username               = var.db_username
  password               = random_password.db.result
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  skip_final_snapshot    = !var.enable_deletion_protection
  deletion_protection    = var.enable_deletion_protection
  publicly_accessible    = false
  multi_az               = var.environment == "prod"

  backup_retention_period = 7
  maintenance_window      = "Mon:03:00-Mon:04:00"
  backup_window           = "02:00-03:00"

  tags = {
    Name = "${local.name_prefix}-postgres"
  }
}
