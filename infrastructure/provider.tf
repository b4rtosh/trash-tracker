terraform {
    required_providers {
        azurerm = {
            source = "hashicorp/azurerm"
            version = "~>4.0"
        }
    }
    backend "azurerm" {
        resource_group_name = "tfstate-rg"
        storage_account_name = "tfstatecaocp"
        container_name = "trash-tracker"
        key = "terraform.tfstate"
        use_oidc = true
    }
}

provider "azurerm" {
    features {}
    client_id = var.client_id
    client_secret = var.client_secret
    tenant_id = var.tenant_id
    subscription_id = var.subscription_id
}