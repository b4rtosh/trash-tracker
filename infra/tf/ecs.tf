resource "aws_ecs_cluster" "this" {
  name = "${var.app-name}-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  container_definitions = jsonencode([{
    name      = "app-container"
    image     = var.app-container-image
    essential = true
    portMappings = [{
      containerPort = 80
      hostPort      = 80
    }]
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
  memory                   = "256"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  container_definitions = jsonencode([{
    name      = "osrm-container"
    image     = var.app-container-image
    essential = true
    portMappings = [{
      containerPort = 5000
      hostPort      = 5000
    }]
    linuxParameters = {
      initProcessEnabled = true
    }
  }])
}

resource "aws_ecs_service" "app" {
  name            = "${var.app-name}-app-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [module.ecs_app_sg.security_group_id]
    assign_public_ip = false
  }
  enable_execute_command = true
}

resource "aws_ecs_service" "osrm" {
  name            = "${var.app-name}-osrm-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.osrm.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = module.vpc.private_subnets
    security_groups  = [module.ecs_osrm_sg.security_group_id]
    assign_public_ip = false
  }
  enable_execute_command = true
}