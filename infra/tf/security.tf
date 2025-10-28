module "alb_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.app-name}-alb-sg"
  description = "Security group for application loadbalancer"
  vpc_id      = module.vpc.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      description = "Request proxied through CloudFlare"
      cidr_blocks = "10.0.0.0/16"
    }
  ]

  egress_with_source_security_group_id = [
    {
      from_port                = 80
      to_port                  = 80
      protocol                 = "tcp"
      description              = "Request redirected to the ECS"
      source_security_group_id = module.ecs_app_sg.security_group_id
    }
  ]
}


module "ecs_app_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.app-name}-ecs-app-sg"
  description = "Security group for ECS app container"
  vpc_id      = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port                = 80
      to_port                  = 80
      protocol                 = "tcp"
      description              = "Request to an app"
      source_security_group_id = module.alb_sg.security_group_id
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = "0.0.0.0/0"
      description = "Allow all outbound traffic"
    }
  ]

  egress_with_source_security_group_id = [
    {
      from_port                = 5000
      to_port                  = 5000
      protocol                 = "tcp"
      description              = "Request to calculate the track by OSRM"
      source_security_group_id = module.ecs_osrm_sg.security_group_id
    }
  ]
}

module "ecs_osrm_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.app-name}-ecs-osrm-sg"
  description = "Security group for ECS OSRM container"
  vpc_id      = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port                = 5000
      to_port                  = 5000
      protocol                 = "tcp"
      description              = "Request from app container"
      source_security_group_id = module.ecs_app_sg.security_group_id
    }
  ]

  egress_with_source_security_group_id = [
    {
      from_port                = 2049
      to_port                  = 2049
      protocol                 = "tcp"
      description              = "NFS access to EFS"
      source_security_group_id = module.efs_sg.security_group_id
    }
  ]
}

module "efs_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.app-name}-efs-sg"
  description = "Security group for EFS volume containing map data"
  vpc_id      = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port                = 2049
      to_port                  = 2049
      protocol                 = "tcp"
      description              = "NFS from OSRM containers"
      source_security_group_id = module.ecs_osrm_sg.security_group_id
    },
    {
      from_port                = 2049
      to_port                  = 2049
      protocol                 = "tcp"
      description              = "NFS from EC2 for data preparation"
      source_security_group_id = module.ec2_sg.security_group_id
    }
  ]
}

module "ec2_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.app-name}-ec2-sg"
  description = "Security group for EC2 to prepare osrm map and volume"
  vpc_id      = module.vpc.vpc_id

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = "0.0.0.0/0"
      description = "Allow all outbound traffic"
    }
  ]
}