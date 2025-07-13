# AI Recipes Generator - Staging Environment Configuration

# Project Configuration
project_name = "ai-recipes-generator"
environment  = "staging"
aws_region   = "us-east-1"

# Networking Configuration
vpc_cidr = "10.0.0.0/16"
public_subnet_cidrs = [
  "10.0.1.0/24",
  "10.0.2.0/24"
]
private_subnet_cidrs = [
  "10.0.3.0/24",
  "10.0.4.0/24"
]

# Database Configuration
db_name                     = "recipes_db"
db_username                 = "recipes_user"
db_instance_class          = "db.t3.micro"
db_allocated_storage       = 20
db_max_allocated_storage   = 50
db_backup_retention_period = 3
db_monitoring_interval     = 0

# ECS Configuration
task_cpu                  = 256
task_memory              = 512
service_desired_count    = 1
autoscaling_min_capacity = 1
autoscaling_max_capacity = 3

# Frontend Configuration
# Leave empty for staging - will use CloudFront default domain
domain_name           = ""
hosted_zone_id        = ""
ssl_certificate_arn   = ""

# Monitoring Configuration
enable_detailed_monitoring = false
log_retention_days        = 7
enable_performance_insights = false
