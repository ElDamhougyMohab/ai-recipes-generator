# AI Recipes Generator - Terraform Outputs

# Networking Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.networking.vpc_id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.networking.public_subnet_ids
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.networking.private_subnet_ids
}

# Database Outputs
output "database_endpoint" {
  description = "Database endpoint"
  value       = module.database.database_endpoint
  sensitive   = true
}

output "database_port" {
  description = "Database port"
  value       = module.database.database_port
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.ecs.cluster_name
}

output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = module.ecs.service_name
}

output "load_balancer_dns_name" {
  description = "DNS name of the load balancer"
  value       = module.ecs.load_balancer_dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = module.ecs.load_balancer_zone_id
}

output "api_url" {
  description = "Backend API URL"
  value       = "https://${module.ecs.load_balancer_dns_name}"
}

# Frontend Outputs
output "frontend_bucket_name" {
  description = "Name of the S3 bucket hosting frontend"
  value       = module.frontend.bucket_name
}

output "cloudfront_distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = module.frontend.cloudfront_distribution_id
}

output "cloudfront_domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = module.frontend.cloudfront_domain_name
}

output "frontend_url" {
  description = "Frontend application URL"
  value       = var.domain_name != "" ? "https://${var.domain_name}" : "https://${module.frontend.cloudfront_domain_name}"
}

# Security Outputs
output "backend_security_group_id" {
  description = "ID of the backend security group"
  value       = module.ecs.backend_security_group_id
}

output "database_security_group_id" {
  description = "ID of the database security group"
  value       = module.database.security_group_id
}

# ECR Repository Output
output "ecr_repository_url" {
  description = "URL of the ECR repository for backend images"
  value       = module.ecs.ecr_repository_url
}

# Parameter Store Outputs
output "parameter_store_paths" {
  description = "Paths to Parameter Store parameters"
  value = {
    gemini_api_key = aws_ssm_parameter.gemini_api_key.name
    database_url   = module.database.database_url_parameter
  }
}

# Resource ARNs for CI/CD
output "task_definition_arn" {
  description = "ARN of the ECS task definition"
  value       = module.ecs.task_definition_arn
}

output "service_arn" {
  description = "ARN of the ECS service"
  value       = module.ecs.service_arn
}

# Deployment Information
output "deployment_info" {
  description = "Summary of deployed resources"
  value = {
    environment   = var.environment
    region        = var.aws_region
    vpc_id        = module.networking.vpc_id
    cluster_name  = module.ecs.cluster_name
    database_name = var.db_name
    frontend_url  = var.domain_name != "" ? "https://${var.domain_name}" : "https://${module.frontend.cloudfront_domain_name}"
    api_url       = "https://${module.ecs.load_balancer_dns_name}"
  }
}
