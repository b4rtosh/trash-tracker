# IAM role for EC2
resource "aws_iam_role" "ec2_osrm_setup" {
  name = "${var.app_name}-ec2-osrm-setup"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_osrm_setup" {
  name = "${var.app_name}-ec2-osrm-setup"
  role = aws_iam_role.ec2_osrm_setup.name
}

# Attach policies for SSM and CloudWatch
resource "aws_iam_role_policy_attachment" "ec2_ssm" {
  role       = aws_iam_role.ec2_osrm_setup.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# OSRM Setup Instance
resource "aws_instance" "osrm_setup" {
  count = var.run_osrm_setup ? 1 : 0

  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = "t2.medium"
  subnet_id     = module.vpc.private_subnets[0]

  vpc_security_group_ids = [module.ec2_sg.security_group_id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_osrm_setup.name

  user_data = base64encode(templatefile("${path.module}/scripts/osrm_setup.sh", {
    efs_id       = aws_efs_file_system.osrm_data.id
    region       = var.aws_region
    map_data_url = var.osrm_map_data_url
  }))

  tags = {
    Name    = "${var.app_name}-osrm-setup"
    Purpose = "OSRM Data Preparation"
  }

  depends_on = [
    aws_efs_mount_target.osrm_target
  ]
}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}