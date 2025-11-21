module "cluster" {
  source = "terraform-aws-modules/rds-aurora/aws"
  version = "9.16.1"
  name          = "${var.app_name}-aurora-cluster"
  database_name = replace(var.app_name, "-", "_")  # Aurora doesn't allow hyphens in DB names

  engine         = "aurora-postgresql"
  engine_version = "17.5"
  instance_class = "db.t4g.medium"  
  instances = {
    one = {}
    # two = {}
  }

  autoscaling_enabled      = true
  autoscaling_min_capacity = 1
  autoscaling_max_capacity = 3

  vpc_id                 = module.vpc.vpc_id
  create_db_subnet_group = true
  subnets                = module.vpc.database_subnets

  # Security Group
  create_security_group = true
  security_group_rules = {
    app_ingress = {
      source_security_group_id = module.ecs_app_sg.security_group_id
      description              = "Allow from ECS app"
    }
  }

  # Master credentials
  master_username = var.db_master_username
  master_password = var.db_master_password

  storage_encrypted   = true
  apply_immediately   = true
  monitoring_interval = 10

  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  skip_final_snapshot = true
  deletion_protection = false
  # Backup configuration
  backup_retention_period      = 7
  preferred_backup_window      = "03:00-04:00"
  preferred_maintenance_window = "mon:04:00-mon:05:00"

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

