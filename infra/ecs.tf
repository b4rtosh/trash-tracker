resource "aws_ecs_cluster" "this" {
  name = "${var.app_name}-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  
  container_definitions = jsonencode([{
    name      = "app-container"
    image     = var.app_container_image
    essential = true
    
    portMappings = [{
      containerPort = 80
      hostPort      = 80
    }]
    
    environment = [
      {
        name  = "DATABASE_HOST"
        value = module.cluster.cluster_endpoint
      },
      {
        name  = "DATABASE_WRITER_HOST"
        value = module.cluster.cluster_endpoint
      },
      {
        name  = "DATABASE_READER_HOST"
        value = module.cluster.cluster_reader_endpoint
      },
      {
        name  = "DATABASE_NAME"
        value = var.app_name
      },
      {
        name  = "DATABASE_USER"
        value = var.db_master_username
      },
      {
        name  = "DATABASE_PORT"
        value = "5432"
      },
      {
        name  = "OSRM_HOST"
        value = "http://${aws_lb.osrm_internal.dns_name}:5000"
      }
    ]
    
    secrets = [
      {
        name      = "DATABASE_PASSWORD"
        valueFrom = aws_secretsmanager_secret.db_password.arn
      }
    ]
    
    linuxParameters = {
      initProcessEnabled = true
    }
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.app.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "app"
      }
    }
  }])
}

# Migration Task Definition - Only needs writer endpoint
resource "aws_ecs_task_definition" "migrate" {
  family                   = "app-migrate-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  
  container_definitions = jsonencode([{
    name      = "migrate-container"
    image     = var.app_container_image
    essential = true
    command   = ["sh", "-c", "python manage.py makemigrations routes && python manage.py migrate"]
    
    environment = [
      {
        name  = "DATABASE_HOST"
        value = module.cluster.cluster_endpoint
      },
      {
        name  = "DATABASE_WRITER_HOST"
        value = module.cluster.cluster_endpoint
      },
      {
        name  = "DATABASE_NAME"
        value = var.app_name
      },
      {
        name  = "DATABASE_USER"
        value = var.db_master_username
      },
      {
        name  = "DATABASE_PORT"
        value = "5432"
      }
    ]
    
    secrets = [
      {
        name      = "DATABASE_PASSWORD"
        valueFrom = aws_secretsmanager_secret.db_password.arn
      }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.migrations.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "migrate"
      }
    }
    
    linuxParameters = {
      initProcessEnabled = true
    }
  }])
}

resource "aws_ecs_task_definition" "osrm" {
  family                   = "osrm-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  
  container_definitions = jsonencode([{
    name      = "osrm-container"
    image     = var.osrm_container_image
    essential = true
    command   = ["osrm-routed", "--algorithm", "mld", "/data/dolnoslaskie-latest.osrm"]
    
    portMappings = [{
      containerPort = 5000
      hostPort      = 5000
      protocol      = "tcp"
    }]

    mountPoints = [{
      sourceVolume  = "map-storage"
      containerPath = "/data"
      readOnly      = true
    }]
    
    linuxParameters = {
      initProcessEnabled = true
    }
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.osrm.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "osrm"
      }
    }
  }])

  volume {
    name = "map-storage"

    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.osrm_data.id
      transit_encryption = "ENABLED"
    }
  }
}

resource "aws_ecs_service" "app" {
  name            = "${var.app_name}-app-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.app_tasks_count
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [module.ecs_app_sg.security_group_id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = module.alb.target_groups["app"].arn
    container_name   = "app-container"
    container_port   = 80
  }
  
  enable_execute_command = true
  
  depends_on = [module.alb]
}

resource "aws_ecs_service" "osrm" {
  name            = "${var.app_name}-osrm-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.osrm.arn
  desired_count   = var.run_osrm_setup ? 0 : var.osrm_tasks_count
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [module.ecs_osrm_sg.security_group_id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.osrm.arn
    container_name   = "osrm-container"
    container_port   = 5000
  }
  
  enable_execute_command = true
  
  depends_on = [
    aws_efs_mount_target.osrm_target,
    aws_lb_listener.osrm_internal
  ]
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/app"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "migrations" {
  name              = "/ecs/migrations"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "osrm" {
  name              = "/ecs/osrm"
  retention_in_days = 7
}

# Reference existing ECR repository (not creating it)
data "aws_ecr_repository" "app" {
  name = "trash-tracker/app"
}