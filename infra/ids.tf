# VPC Flow Logs for network traffic analysis
resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_log_role.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = module.vpc.vpc_id

  tags = {
    Name = "${var.app_name}-flow-logs"
  }
}

resource "aws_cloudwatch_log_group" "flow_logs" {
  name              = "/vpc/${var.app_name}-flow-logs"
  retention_in_days = 7  # Keep short to minimize costs

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

resource "aws_iam_role" "flow_log_role" {
  name = "${var.app_name}-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "flow_log_policy" {
  name = "${var.app_name}-flow-log-policy"
  role = aws_iam_role.flow_log_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ]
      Resource = "*"
    }]
  })
}

# CloudWatch Metric Filters for suspicious activity detection
resource "aws_cloudwatch_log_metric_filter" "rejected_connections" {
  name           = "rejected-connections"
  pattern        = "[version, account, eni, source, destination, srcport, destport, protocol, packets, bytes, windowstart, windowend, action=\"REJECT\", flowlogstatus]"
  log_group_name = aws_cloudwatch_log_group.flow_logs.name

  metric_transformation {
    name      = "RejectedConnectionCount"
    namespace = "${var.app_name}/IDS"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "ssh_attempts" {
  name           = "ssh-connection-attempts"
  pattern        = "[version, account, eni, source, destination, srcport, destport=\"22\", protocol=\"6\", packets, bytes, windowstart, windowend, action, flowlogstatus]"
  log_group_name = aws_cloudwatch_log_group.flow_logs.name

  metric_transformation {
    name      = "SSHAttemptCount"
    namespace = "${var.app_name}/IDS"
    value     = "1"
  }
}

resource "aws_cloudwatch_log_metric_filter" "port_scan_detection" {
  name           = "port-scan-detection"
  pattern        = "[version, account, eni, source, destination, srcport, destport, protocol=\"6\", packets=\"1\", bytes, windowstart, windowend, action=\"REJECT\", flowlogstatus]"
  log_group_name = aws_cloudwatch_log_group.flow_logs.name

  metric_transformation {
    name      = "PortScanAttempts"
    namespace = "${var.app_name}/IDS"
    value     = "1"
  }
}

# Alarms for suspicious activity
resource "aws_cloudwatch_metric_alarm" "high_rejected_connections" {
  alarm_name          = "${var.app_name}-high-rejected-connections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "RejectedConnectionCount"
  namespace           = "${var.app_name}/IDS"
  period              = 300
  statistic           = "Sum"
  threshold           = 100
  alarm_description   = "High number of rejected connections - possible attack"
  
  alarm_actions = [aws_sns_topic.ids_alerts.arn]

  tags = {
    Environment = "production"
  }
}

resource "aws_cloudwatch_metric_alarm" "port_scan_alarm" {
  alarm_name          = "${var.app_name}-port-scan-detected"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "PortScanAttempts"
  namespace           = "${var.app_name}/IDS"
  period              = 60
  statistic           = "Sum"
  threshold           = 50
  alarm_description   = "Possible port scan detected"
  
  alarm_actions = [aws_sns_topic.ids_alerts.arn]

  tags = {
    Environment = "production"
  }
}

# SNS Topic for alerts
resource "aws_sns_topic" "ids_alerts" {
  name = "${var.app_name}-security-alerts"

  tags = {
    Environment = "production"
  }
}

resource "aws_sns_topic_subscription" "ids_email" {
  topic_arn = aws_sns_topic.ids_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}