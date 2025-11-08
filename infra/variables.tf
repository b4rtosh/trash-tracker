variable "aws_region" {
  description = "Deployment region"
  type        = string
  default     = "eu-central-1"
}

variable "app_name" {
  description = "Name of an app"
  type        = string
  default     = "trash-tracker"
}

variable "app_container_image" {
  description = "Docker image for the app container"
  type        = string
}

variable "osrm_container_image" {
  description = "Docker image for the OSRM container"
  type        = string
}

variable "aws_profile" {
  description = "Profile to login to AWS"
  type        = string
  default     = "terraform"
}

variable "db_master_username" {
  description = "Master username for admin only"
  type        = string
  sensitive   = true
}

variable "db_master_password" {
  description = "Master password for admin only"
  type        = string
  sensitive   = true
}

variable "osrm_map_data_url" {
  description = "URL to download OSRM map data"
  type        = string
  default     = "https://download.geofabrik.de/europe/poland/dolnoslaskie-latest.osm.pbf"
}

variable "run_osrm_setup" {
  description = "Whether to launch EC2 instance for OSRM data preparation"
  type        = bool
  default     = false
}

variable "app_tasks_count" {
  description = "Amount of app tasks"
  type        = number
  default     = 2
}

variable "osrm_tasks_count" {
  description = "Amount of osrm tasks"
  type        = number
  default     = 2
}

variable "domain_name" {
  description = "Domain name for SSL certificate"
  type        = string
  default     = "trash-tracker.example.com"  # Change to your domain
}

variable "run_migrations" {
  description = "Whether to run migrations on app startup"
  type        = bool
  default     = false
}