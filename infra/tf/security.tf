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
      source_security_group_id = module.ecs_sg.security_group_id
    }
  ]
}


module "ecs_sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.app-name}-ecs-sg"
  description = "Security group for ecs"
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
}

