resource "random_password" "db" {
  length  = 32
  special = false
}

resource "aws_secretsmanager_secret" "db_url" {
  name        = "${local.name_prefix}-db-url"
  description = "PostgreSQL connection URL for ${local.name_prefix}"
}

resource "aws_secretsmanager_secret_version" "db_url" {
  secret_id = aws_secretsmanager_secret.db_url.id
  secret_string = format(
    "postgresql+psycopg2://%s:%s@%s:%s/%s",
    var.db_username,
    random_password.db.result,
    aws_db_instance.postgres.address,
    aws_db_instance.postgres.port,
    aws_db_instance.postgres.db_name
  )
}

resource "aws_secretsmanager_secret" "backend_secret_key" {
  name        = "${local.name_prefix}-backend-secret-key"
  description = "JWT secret key for ${local.name_prefix} backend"
}

resource "aws_secretsmanager_secret_version" "backend_secret_key" {
  secret_id     = aws_secretsmanager_secret.backend_secret_key.id
  secret_string = var.backend_secret_key
}

resource "aws_secretsmanager_secret" "llm" {
  count       = var.llm_api_key != "" ? 1 : 0
  name        = "${local.name_prefix}-llm-api-key"
  description = "API key for the LLM provider used by ${local.name_prefix} agents"
}

resource "aws_secretsmanager_secret_version" "llm" {
  count         = var.llm_api_key != "" ? 1 : 0
  secret_id     = aws_secretsmanager_secret.llm[0].id
  secret_string = var.llm_api_key
}
