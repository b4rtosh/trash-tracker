resource "aws_secretsmanager_secret" "django_superuser" {
  name                    = "${var.app_name}-django-superuser"
  recovery_window_in_days = 7

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "django_superuser" {
  secret_id     = aws_secretsmanager_secret.django_superuser.id
  secret_string = jsonencode({
    username = var.django_superuser_username
    email    = var.django_superuser_email
    password = var.django_superuser_password
  })
}