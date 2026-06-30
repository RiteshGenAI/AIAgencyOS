# Placeholder RDS definition. Fill with subnet group, parameter group, etc.

resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  name                 = "agency_os"
  username             = "postgres"
  password             = "change-me"
  skip_final_snapshot  = true
}
