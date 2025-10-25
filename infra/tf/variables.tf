variable "tf-state-bucket" {
  description = "Name of terraform state bucket"
  type        = string
}

variable "tf-state-key" {
  description = "Key of terraform state file"
  type        = string
}

variable "region" {
  description = "Deployment region"
  type        = string
}

variable "app-name" {
  description = "Name of an app"
  type        = string
  default     = "trash-tracker"
}