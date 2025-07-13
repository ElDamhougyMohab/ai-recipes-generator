# AI Recipes Generator - Production Environment Configuration

# Project Configuration
project_name = "ai-recipes-generator"
environment  = "production"
aws_region   = "us-east-1"

# Networking Configuration
vpc_cidr = "10.1.0.0/16"
public_subnet_cidrs = [
  "10.1.1.0/24",
  "10.1.2.0/24"
]
private_subnet_cidrs = [
  "10.1.3.0/24",
  "10.1.4.0/24"
]

# Database Configuration
db_name                     = "recipes_db"
db_username                 = "recipes_user"
db_instance_class          = "db.t3.small"
db_allocated_storage       = 50
db_max_allocated_storage   = 200
db_backup_retention_period = 7
db_monitoring_interval     = 60

# ECS Configuration
task_cpu                  = 512
task_memory              = 1024
service_desired_count    = 2
autoscaling_min_capacity = 2
autoscaling_max_capacity = 10

# Frontend Configuration
# Replace with your actual domain configuration
domain_name           = "recipes.yourdomain.com"
hosted_zone_id        = "Z1234567890ABC"  # Replace with your Route 53 hosted zone ID
ssl_certificate_arn   = "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"  # Replace with your ACM certificate ARN

# Monitoring Configuration
enable_detailed_monitoring = true
log_retention_days        = 30
enable_performance_insights = true
