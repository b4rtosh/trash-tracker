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

  ingress_cidr_blocks = ["0.0.0.0/0"]
  ingress_rules       = ["https-443-tcp"]
  
  egress_rules = ["all-all"]
}

module "ec2_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = "${var.app_name}-ec2-sg"
  description = "Security group for EC2 OSRM setup instance"
  vpc_id      = module.vpc.vpc_id

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
    },
    {
      from_port                = 2049
      to_port                  = 2049
      protocol                 = "tcp"
      description              = "NFS from EC2"
      source_security_group_id = module.ec2_sg.security_group_id
    }
  ]

  egress_rules = ["all-all"]
}