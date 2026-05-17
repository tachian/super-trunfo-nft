module "platform" {
  source = "../../modules/platform"

  project_name      = "super-trunfo"
  environment       = "staging"
  region            = var.region
  db_password       = var.db_password
  rabbitmq_password = var.rabbitmq_password
  node_min_size     = 2
  node_desired_size = 2
  node_max_size     = 4
}

output "cluster_name" {
  value = module.platform.cluster_name
}

output "assets_bucket" {
  value = module.platform.assets_bucket
}

