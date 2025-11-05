terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  # backend "s3" {
  #   bucket = var.tf-state-bucket
  #   key    = var.tf-state-key
  #   region = var.region
  # }

  required_version = ">= 1.2"
}