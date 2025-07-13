# AI Recipes Generator - Main Terraform Configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }

  # Remote state configuration
  backend "s3" {
    bucket         = "ai-recipes-terraform-state-072950892577"
    key            = "ai-recipes-generator/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "ai-recipes-terraform-locks"
    encrypt        = true
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "AI-Recipes-Generator"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "ElDamhougyMohab"
    }
  }
}

# Random suffix for unique resource names
resource "random_id" "suffix" {
  byte_length = 4
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Networking Module
module "networking" {
  source = "./modules/networking"

  project_name          = var.project_name
  environment           = var.environment
  vpc_cidr              = var.vpc_cidr
  public_subnet_cidrs   = var.public_subnet_cidrs
  private_subnet_cidrs  = var.private_subnet_cidrs
}

# Database Module
module "database" {
  source = "./modules/database"

  project_name               = var.project_name
  environment                = var.environment
  private_subnet_ids         = module.networking.private_subnet_ids
  database_security_group_id = module.networking.database_security_group_id
  db_name                    = var.db_name
  db_username                = var.db_username
  db_password                = var.db_password
  db_instance_class         = var.db_instance_class
  db_allocated_storage      = var.db_allocated_storage
  db_max_allocated_storage  = var.db_max_allocated_storage
  db_backup_retention_period = var.db_backup_retention_period
  db_backup_window          = var.db_backup_window
  db_maintenance_window     = var.db_maintenance_window
  db_monitoring_interval    = var.db_monitoring_interval
}

# ECS Module (Backend)
module "ecs" {
  source = "./modules/ecs"
  
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region
  account_id   = data.aws_caller_identity.current.account_id
  
  vpc_id                     = module.networking.vpc_id
  public_subnet_ids          = module.networking.public_subnet_ids
  private_subnet_ids         = module.networking.private_subnet_ids
  alb_security_group_id      = module.networking.alb_security_group_id
  ecs_security_group_id      = module.networking.ecs_security_group_id
  
  task_cpu                   = var.backend_cpu
  task_memory                = var.backend_memory
  service_desired_count      = var.backend_desired_count
  autoscaling_min_capacity   = var.min_capacity
  autoscaling_max_capacity   = var.max_capacity
}

# Frontend Module (S3 + CloudFront)
module "frontend" {
  source = "./modules/frontend"
  
  project_name = var.project_name
  environment  = var.environment
  domain_name  = var.domain_name
  
  alb_dns_name = module.ecs.load_balancer_dns_name
}

# Parameter Store for sensitive data
resource "aws_ssm_parameter" "gemini_api_key" {
  name  = "/${var.project_name}/${var.environment}/gemini_api_key"
  type  = "SecureString"
  value = var.gemini_api_key

  tags = {
    Project     = "AI-Recipes-Generator"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
