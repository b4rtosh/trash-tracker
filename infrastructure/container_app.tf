
resource "azurerm_container_app_environment" "environment" {
  name                       = "${var.app_name}-app-${var.env}"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.log.id
}

resource "azurerm_container_app" "example" {
  name                         = "${app_name}-app"
  container_app_environment_id = azurerm_container_app_environment.environment.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {
    container {
      name   = "osrm"
      image  = "osrm/osrm-backend"
      cpu    = 0.25
      memory = "0.5Gi"
    }
  }
} 

resource "azurerm_storage_account" "app" {
  name = "${app_name}-sa-"
  resource_group_name =  azurerm_resource_group.rg.name
  location = azurerm_resource_group.rg.location
  account_tier = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_file_share" "osrm" {
  name = "${var.app_name}-fs-${var.env}"
  storage_account_id = azurerm_storage_account.app.id
  quota = 5
}