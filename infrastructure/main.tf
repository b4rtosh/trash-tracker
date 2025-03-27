locals {
  stack = "${var.app_name}-${var.env}"

  default_tags = {
    environment = var.env
    owner       = "b4rtosh"
    app         = var.app_name
  }
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-${local.stack}"
  location = var.region

  tags = local.default_tags
}

resource "azurerm_log_analytics_workspace" "app" {
  name                = "log-${local.stack}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  tags = local.default_tags
}
