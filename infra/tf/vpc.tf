module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "6.5.0"

  name = "${var.app-name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
  one_nat_gateway_per_az = false
  
  create_database_subnet_group = true
  database_subnets = ["10.0.201.0/24", "10.0.202.0/24"]
  
  enable_dns_hostnames = true
  enable_dns_support = true

  # Subnets tags
  public_subnet_tags = {
    Type = "public-subnets"
  }
  private_subnet_tags = {
    Type = "private-subnets"
  }
  database_subnet_tags = {
    Type = "database-subnets"
  }
  
  tags = {
    Terraform = "true"
    Environment = "prd"
  }
  vpc_tags = {
    Type = "vpc-prd"
  }
}