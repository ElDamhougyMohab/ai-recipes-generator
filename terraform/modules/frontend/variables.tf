# AI Recipes Generator - Frontend Module Variables

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the frontend (optional)"
  type        = string
  default     = ""
}

variable "hosted_zone_id" {
  description = "Route 53 hosted zone ID (required if domain_name is provided)"
  type        = string
  default     = ""
}

variable "ssl_certificate_arn" {
  description = "ARN of SSL certificate in ACM (required if domain_name is provided)"
  type        = string
  default     = ""
}

variable "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  type        = string
  default     = ""
}
