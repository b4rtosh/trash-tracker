output "aurora_cluster_endpoint" {
  description = "Writer endpoint for the Aurora cluster"
  value       = module.cluster.cluster_endpoint
}

output "aurora_reader_endpoint" {
  description = "Reader endpoint for the Aurora cluster"
  value       = module.cluster.cluster_reader_endpoint
}

output "rds_port" {
  description = "RDS instance port"
  value       = module.cluster.cluster_port
  sensitive   = true
}

output "rds_username" {
  description = "RDS instance root username"
  value       = module.cluster.cluster_master_username
  sensitive   = true
}

output "efs_file_system_id" {
  description = "ID of the EFS file system for OSRM data"
  value       = aws_efs_file_system.osrm_data.id
}

output "efs_mount_target_ids" {
  description = "IDs of EFS mount targets"
  value       = aws_efs_mount_target.osrm_target[*].id
}

output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.this.name
}

output "private_subnets" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnets
}

output "app_security_group_id" {
  description = "App security group ID"
  value       = module.ecs_app_sg.security_group_id
}

output "database_endpoint" {
  description = "Aurora cluster endpoint (writer)"
  value       = module.cluster.cluster_endpoint
  sensitive   = true
}

output "database_reader_endpoint" {
  description = "Aurora cluster reader endpoint"
  value       = module.cluster.cluster_reader_endpoint
  sensitive   = true
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = module.alb.dns_name
}

output "osrm_internal_dns" {
  description = "OSRM internal load balancer DNS"
  value       = aws_lb.osrm_internal.dns_name
}

# Reference existing ECR repository instead of creating it
output "ecr_repository_name" {
  description = "ECR repository name"
  value       = data.aws_ecr_repository.app.name
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = data.aws_ecr_repository.app.repository_url
}