resource "aws_efs_file_system" "osrm_data" {
  creation_token = "${var.app-name}-osrm-data"
  encrypted      = true

  tags = {
    Name = "OSRMData"
  }
}

resource "aws_efs_mount_target" "osrm_target" {
  count = length(module.vpc.private_subnets)
  
  file_system_id  = aws_efs_file_system.osrm_data.id
  subnet_id       = module.vpc.private_subnets[count.index]
  security_groups = [module.efs_sg.security_group_id]
}

output "efs_file_system_id" {
  description = "ID of the EFS file system for OSRM data"
  value       = aws_efs_file_system.osrm_data.id
}

output "efs_mount_target_ids" {
  description = "IDs of EFS mount targets"
  value       = aws_efs_mount_target.osrm_target[*].id
}