module "ecs_app_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "${var.app_name}-ecs-app-sg"
  description = "Security group for ECS app tasks"
  vpc_id      = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port                = 8080
      to_port                  = 8080
      protocol                 = "tcp"
      description              = "HTTP from ALB"
      source_security_group_id = module.alb_sg.security_group_id
    }
  ]

  egress_rules = ["all-all"]
}

module "ecs_osrm_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "${var.app_name}-ecs-osrm-sg"
  description = "Security group for ECS OSRM tasks"
  vpc_id      = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port                = 5000
      to_port                  = 5000
      protocol                 = "tcp"
      description              = "OSRM from app"
      source_security_group_id = module.ecs_app_sg.security_group_id
    },
    {
      from_port                = 5000
      to_port                  = 5000
      protocol                 = "tcp"
      description              = "OSRM from lb"
      source_security_group_id = module.osrm_internal_alb_sg.security_group_id
    }
  ]

  egress_rules = ["all-all"]
}

module "alb_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "${var.app_name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = module.vpc.vpc_id

  ingress_cidr_blocks = local.cloudflare_ips
  ingress_rules       = ["https-443-tcp", "http-80-tcp"]
  
  egress_rules = ["all-all"]
}

module "efs_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "${var.app_name}-efs-sg"
  description = "Security group for EFS"
  vpc_id      = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port                = 2049
      to_port                  = 2049
      protocol                 = "tcp"
      description              = "NFS from ECS OSRM"
      source_security_group_id = module.ecs_osrm_sg.security_group_id
    }
  ]

  egress_rules = ["all-all"]
}

module "osrm_internal_alb_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "${var.app_name}-osrm-internal-alb-sg"
  description = "Security group for internal OSRM load balancer"
  vpc_id      = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port                = 5000
      to_port                  = 5000
      protocol                 = "tcp"
      description              = "OSRM from app tasks"
      source_security_group_id = module.ecs_app_sg.security_group_id
    }
  ]

  egress_rules = ["all-all"]
}

locals {
  cloudflare_ips = [
    "173.245.48.0/20",
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "141.101.64.0/18",
    "108.162.192.0/18",
    "190.93.240.0/20",
    "188.114.96.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17",
    "162.158.0.0/15",
    "104.16.0.0/13",
    "104.24.0.0/14",
    "172.64.0.0/13",
    "131.0.72.0/22"
  ]
}