# AI Recipes Generator - Terraform Variables

# Project Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "ai-recipes-generator"
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be either 'staging' or 'production'."
  }
}

# Infrastructure Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

# Database Configuration
variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "airecipes"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "airecipes_admin"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS instance in GB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum allocated storage for RDS instance in GB"
  type        = number
  default     = 100
}

variable "db_backup_retention_period" {
  description = "Backup retention period for RDS instance in days"
  type        = number
  default     = 7
}

variable "db_backup_window" {
  description = "Backup window for RDS instance"
  type        = string
  default     = "03:00-04:00"
}

variable "db_maintenance_window" {
  description = "Maintenance window for RDS instance"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "db_monitoring_interval" {
  description = "Monitoring interval for RDS instance"
  type        = number
  default     = 60
}

variable "backup_retention_period" {
  description = "Backup retention period for RDS instance in days"
  type        = number
  default     = 7
}

variable "enable_multi_az" {
  description = "Enable Multi-AZ for RDS instance"
  type        = bool
  default     = false
}

# Container Configuration
variable "backend_image" {
  description = "Docker image for backend service"
  type        = string
  default     = "nginx:latest"
}

variable "backend_cpu" {
  description = "CPU units for backend container"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Memory for backend container in MB"
  type        = number
  default     = 512
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 1
}

# Auto Scaling Configuration
variable "enable_auto_scaling" {
  description = "Enable auto scaling for ECS service"
  type        = bool
  default     = false
}

variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 10
}

# Frontend Configuration
variable "domain_name" {
  description = "Domain name for the application (optional)"
  type        = string
  default     = ""
}

variable "create_certificate" {
  description = "Create SSL certificate for domain"
  type        = bool
  default     = false
}

# Application Configuration
variable "gemini_api_key" {
  description = "Google Gemini API key"
  type        = string
  sensitive   = true
}

# Monitoring Configuration
variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring and alarms"
  type        = bool
  default     = false
}

variable "enable_logging" {
  description = "Enable CloudWatch logging"
  type        = bool
  default     = true
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Use Spot instances for cost optimization (staging only)"
  type        = bool
  default     = false
}
