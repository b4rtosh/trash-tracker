variable "region" {
    type = string
    description = "The location of the resource group"
}

variable "client_id" {
    type = string
    description = "The client id of the service principal"
    sensitive = true
}

variable "client_secret" {
    type = string
    description = "The client secret of the service principal"
    sensitive = true
}

variable "tenant_id" {
    type = string
    description = "The tenant id of the service principal"
    sensitive = true
}

variable "subscription_id" {
    type = string
    description = "The subscription id of the service principal"
    sensitive = true
}

variable "backend_resource_group_name" {
    type = string
    description = "The name of the resource group for the backend"
}

variable "backend_storage_account_name" {
    type = string
    description = "The name of the storage account for the backend"
}

variable "backend_container_name" {
    type = string
    description = "The name of the container for the backend"
}

variable "backend_key" {
    type = string
    description = "The key for the backend"
}

variable "resource_group_name" {
    type = string
}

variable "app_name" {
    type = string
}

variable "env" {
    type = string
}