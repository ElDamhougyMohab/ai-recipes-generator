# AI Recipes Generator - Database Module Outputs

output "database_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "database_port" {
  description = "Database port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "Database username"
  value       = aws_db_instance.main.username
}

output "database_password_parameter" {
  description = "Parameter Store path for database password"
  value       = aws_ssm_parameter.db_password.name
}

output "database_url_parameter" {
  description = "Parameter Store path for database URL"
  value       = aws_ssm_parameter.database_url.name
}

output "database_instance_id" {
  description = "Database instance ID"
  value       = aws_db_instance.main.id
}

output "database_arn" {
  description = "Database ARN"
  value       = aws_db_instance.main.arn
}

output "security_group_id" {
  description = "Database security group ID"
  value       = var.database_security_group_id
}

output "subnet_group_name" {
  description = "Database subnet group name"
  value       = aws_db_subnet_group.main.name
}

output "read_replica_endpoint" {
  description = "Read replica endpoint (if exists)"
  value       = var.environment == "production" ? aws_db_instance.read_replica[0].endpoint : null
}
