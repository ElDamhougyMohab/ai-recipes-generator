# AI Recipes Generator - Database Module

# Generate random password for database
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store database password in AWS Parameter Store
resource "aws_ssm_parameter" "db_password" {
  name  = "/${var.project_name}/${var.environment}/db_password"
  type  = "SecureString"
  value = random_password.db_password.result

  tags = {
    Name        = "${var.project_name}-db-password-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-db-subnet-group-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# DB Parameter Group
resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "${var.project_name}-db-params-${var.environment}"

  parameter {
    name  = "log_statement"
    value = "all"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  tags = {
    Name        = "${var.project_name}-db-params-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-db-${var.environment}"
  engine         = "postgres"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [var.database_security_group_id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name

  backup_retention_period = var.db_backup_retention_period
  backup_window          = var.db_backup_window
  maintenance_window     = var.db_maintenance_window

  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-db-final-snapshot-${var.environment}-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  deletion_protection = var.environment == "production"

  monitoring_interval = var.db_monitoring_interval
  monitoring_role_arn = var.db_monitoring_interval > 0 ? aws_iam_role.rds_monitoring[0].arn : null

  performance_insights_enabled = var.environment == "production"
  performance_insights_retention_period = var.environment == "production" ? 7 : null

  auto_minor_version_upgrade = true
  allow_major_version_upgrade = false

  tags = {
    Name        = "${var.project_name}-db-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# RDS Monitoring Role (only created if monitoring is enabled)
resource "aws_iam_role" "rds_monitoring" {
  count = var.db_monitoring_interval > 0 ? 1 : 0

  name = "${var.project_name}-rds-monitoring-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-rds-monitoring-role-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Attach the AWS managed policy for RDS monitoring
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  count = var.db_monitoring_interval > 0 ? 1 : 0

  role       = aws_iam_role.rds_monitoring[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Log Group for RDS
resource "aws_cloudwatch_log_group" "rds_log_group" {
  name              = "/aws/rds/instance/${aws_db_instance.main.id}/postgresql"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-rds-logs-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# RDS Subnet Group for read replicas (if needed in production)
resource "aws_db_subnet_group" "read_replica" {
  count = var.environment == "production" ? 1 : 0

  name       = "${var.project_name}-read-replica-subnet-group-${var.environment}"
  subnet_ids = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-read-replica-subnet-group-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Read Replica (only for production)
resource "aws_db_instance" "read_replica" {
  count = var.environment == "production" ? 1 : 0

  identifier             = "${var.project_name}-db-read-replica-${var.environment}"
  replicate_source_db    = aws_db_instance.main.identifier
  instance_class         = var.db_instance_class
  publicly_accessible    = false
  auto_minor_version_upgrade = true

  vpc_security_group_ids = [var.database_security_group_id]

  tags = {
    Name        = "${var.project_name}-db-read-replica-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}

# Database URL for application
locals {
  database_url = "postgresql://${var.db_username}:${random_password.db_password.result}@${aws_db_instance.main.endpoint}:${aws_db_instance.main.port}/${var.db_name}"
}

# Store database URL in Parameter Store
resource "aws_ssm_parameter" "database_url" {
  name  = "/${var.project_name}/${var.environment}/database_url"
  type  = "SecureString"
  value = local.database_url

  tags = {
    Name        = "${var.project_name}-database-url-${var.environment}"
    Project     = var.project_name
    Environment = var.environment
  }
}
