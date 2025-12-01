resource "aws_cloudwatch_log_group" "waf_log_group" {
  name              = "aws-waf-logs-${var.app_name}"
  retention_in_days = 7

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

resource "aws_wafv2_web_acl" "default" {
  name        = "${var.app_name}-web-acl"
  description = "WAF custom rules for ALB"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "WAF_Custom_Protections"
    sampled_requests_enabled   = true
  }

  # Rule 1: Block SQL Injection patterns
  rule {
    name     = "SQLInjectionRule"
    priority = 0
    action {
      block {}
    }
    statement {
      or_statement {
        # Query string checks
        statement {
          byte_match_statement {
            search_string = "union select"
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        # Body checks for SQL injection
        statement {
          byte_match_statement {
            search_string = "union select"
            field_to_match {
              body {
                oversize_handling = "MATCH"
              }
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "' or '"
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "' or '"
            field_to_match {
              body {
                oversize_handling = "MATCH"
              }
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "1=1"
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "1=1"
            field_to_match {
              body {
                oversize_handling = "MATCH"
              }
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "drop table"
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "drop table"
            field_to_match {
              body {
                oversize_handling = "MATCH"
              }
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "SQLInjectionRule"
      sampled_requests_enabled   = true
    }
  }

  # Rule 2: Block XSS patterns
  rule {
    name     = "XSSRule"
    priority = 1
    action {
      block {}
    }
    statement {
      or_statement {
        statement {
          byte_match_statement {
            search_string = "<script"
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "javascript:"
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "onerror="
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "onload="
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "XSSRule"
      sampled_requests_enabled   = true
    }
  }

  # Rule 3: Block IP addresses in URI (path traversal/SSRF attempts)
  rule {
    name     = "BlockIPInURIRule"
    priority = 2
    action {
      block {}
    }
    statement {
      or_statement {
        statement {
          regex_match_statement {
            regex_string = "\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}"
            field_to_match {
              uri_path {}
            }
            text_transformation {
              priority = 0
              type     = "NONE"
            }
          }
        }
        statement {
          byte_match_statement {
            search_string = "127.0.0.1"
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
        statement {
          byte_match_statement {
            search_string = "localhost"
            field_to_match {
              query_string {}
            }
            text_transformation {
              priority = 0
              type     = "LOWERCASE"
            }
            positional_constraint = "CONTAINS"
          }
        }
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "BlockIPInURIRule"
      sampled_requests_enabled   = true
    }
  }

  # Rule 4: Rate limiting (5 mins evaluation window)
  rule {
    name     = "RateLimitRule"
    priority = 3
    action {
      block {}
    }
    statement {
      rate_based_statement {
        limit              = var.request_rate_limit
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }

#   # Rule 5: Geo-blocking (only Poland allowed)
#   rule {
#     name     = "GeoBlockRule"
#     priority = 4
#     action {
#       block {}
#     }
#     statement {
#       not_statement {
#         statement {
#           geo_match_statement {
#             country_codes = ["PL"]
#           }
#         }
#       }
#     }
#     visibility_config {
#       cloudwatch_metrics_enabled = true
#       metric_name                = "GeoBlockRule"
#       sampled_requests_enabled   = true
#     }
#   }
}

# WAF logging
resource "aws_wafv2_web_acl_logging_configuration" "waf_logging" {
  log_destination_configs = [aws_cloudwatch_log_group.waf_log_group.arn]
  resource_arn            = aws_wafv2_web_acl.default.arn

  redacted_fields {
    uri_path {}
  }
}

# WAF association
resource "aws_wafv2_web_acl_association" "alb_association" {
  resource_arn = module.alb.arn
  web_acl_arn  = aws_wafv2_web_acl.default.arn
}


variable "request_rate_limit" {
  type = number
  description = "Number of allowed requests in 5 mins window"
  default = 20
  validation {
    condition     = var.request_rate_limit < 100
    error_message = "Requests rate limits has to be lower than 100"
  }
}