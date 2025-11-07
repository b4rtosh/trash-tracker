resource "aws_secretsmanager_secret" "db_password" {
  name                    = "${var.app_name}-db-master-password"
  recovery_window_in_days = 7
  
  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_master_password
}