# SNS Topic for alerts
resource "aws_sns_topic" "ids_alerts" {
  name = "${var.app_name}-security-alerts"

  tags = {
    Environment = "production"
  }
}

locals {
  alert_emails = split(",", var.alert_email)
}

resource "aws_sns_topic_subscription" "ids_email" {
  for_each  = toset(local.alert_emails)
  topic_arn = aws_sns_topic.ids_alerts.arn
  protocol  = "email"
  endpoint  = trimspace(each.value)
}