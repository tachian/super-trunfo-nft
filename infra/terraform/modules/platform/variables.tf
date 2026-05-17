variable "project_name" {
  type        = string
  description = "Project name used for resources and tags."
}

variable "environment" {
  type        = string
  description = "Deployment environment."
}

variable "region" {
  type        = string
  description = "AWS region."
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block."
  default     = "10.42.0.0/16"
}

variable "cluster_version" {
  type        = string
  description = "EKS Kubernetes version."
  default     = "1.31"
}

variable "node_instance_types" {
  type        = list(string)
  description = "Managed node group instance types."
  default     = ["t3.large"]
}

variable "node_min_size" {
  type        = number
  description = "Minimum EKS node count."
  default     = 2
}

variable "node_max_size" {
  type        = number
  description = "Maximum EKS node count."
  default     = 6
}

variable "node_desired_size" {
  type        = number
  description = "Desired EKS node count."
  default     = 2
}

variable "db_username" {
  type        = string
  description = "PostgreSQL administrator username."
  default     = "super_trunfo"
}

variable "db_password" {
  type        = string
  description = "PostgreSQL administrator password."
  sensitive   = true
}

variable "db_instance_class" {
  type        = string
  description = "RDS instance class."
  default     = "db.t4g.medium"
}

variable "redis_node_type" {
  type        = string
  description = "ElastiCache node type."
  default     = "cache.t4g.small"
}

variable "rabbitmq_username" {
  type        = string
  description = "RabbitMQ administrator username."
  default     = "super_trunfo"
}

variable "rabbitmq_password" {
  type        = string
  description = "RabbitMQ administrator password."
  sensitive   = true
}

