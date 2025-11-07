module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

  name    = "${var.app_name}-alb-app"
  vpc_id  = module.vpc.vpc_id
  subnets = module.vpc.public_subnets

  security_group_ingress_rules = {
    cloudflare_https = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      description = "HTTPS from Cloudflare"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }
  
  security_group_egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = "10.0.0.0/16"
    }
  }

  listeners = {
    https = {
      port            = 443
      protocol        = "HTTPS"
      certificate_arn = aws_acm_certificate.self_signed.arn
      ssl_policy      = "ELBSecurityPolicy-TLS13-1-2-2021-06"
      
      forward = {
        target_group_key = "app"
      }
    }
  }

  target_groups = {
    app = {
      name_prefix      = "app-"
      protocol         = "HTTP"
      port             = 80
      target_type      = "ip"
      vpc_id           = module.vpc.vpc_id
      create_attachment = false
      
      health_check = {
        enabled             = true
        healthy_threshold   = 2
        interval            = 30
        matcher             = "200"
        path                = "/"
        port                = "traffic-port"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 2
      }
      
      deregistration_delay = 30
      
      stickiness = {
        enabled = true
        type    = "lb_cookie"
      }
    }
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

# Generate self-signed certificate - REPLACES your current cert resources
resource "tls_private_key" "alb" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "alb" {
  private_key_pem = tls_private_key.alb.private_key_pem

  subject {
    common_name  = var.domain_name
    organization = "Trash Tracker"
  }

  validity_period_hours = 87600 # 10 years

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

# Import self-signed cert into ACM
resource "aws_acm_certificate" "self_signed" {
  private_key      = tls_private_key.alb.private_key_pem
  certificate_body = tls_self_signed_cert.alb.cert_pem

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

# Internal Load Balancer for OSRM (this part is OK)
resource "aws_lb" "osrm_internal" {
  name               = "${var.app_name}-osrm-internal"
  internal           = true
  load_balancer_type = "application"
  security_groups    = [module.ecs_osrm_sg.security_group_id]
  subnets            = module.vpc.private_subnets

  tags = {
    Name = "${var.app_name}-osrm-internal"
  }
}

resource "aws_lb_target_group" "osrm" {
  name        = "${var.app_name}-osrm-tg"
  port        = 5000
  protocol    = "HTTP"
  vpc_id      = module.vpc.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 5
    unhealthy_threshold = 2
  }

  tags = {
    Name = "${var.app_name}-osrm-tg"
  }
}

resource "aws_lb_listener" "osrm_internal" {
  load_balancer_arn = aws_lb.osrm_internal.arn
  port              = "5000"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.osrm.arn
  }
}