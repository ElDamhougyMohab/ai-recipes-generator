# AI Recipes Generator - Terraform README

## Prerequisites

1. **AWS CLI Configuration**
   ```bash
   aws configure
   # Enter your AWS Access Key ID, Secret Access Key, and Region
   ```

2. **Terraform Installation**
   - Download from https://terraform.io/downloads.html
   - Add to PATH

3. **Required AWS Permissions**
   - VPC, EC2, RDS, ECS, ECR, S3, CloudFront, Route 53, IAM, SSM, CloudWatch

## Initial Setup

### 1. Configure Backend Storage

First, create an S3 bucket for Terraform state:

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://ai-recipes-terraform-state-YOUR-ACCOUNT-ID

# Create DynamoDB table for state locking
aws dynamodb create-table \
    --table-name ai-recipes-terraform-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

### 2. Update Backend Configuration

Edit `main.tf` and update the backend configuration:

```hcl
backend "s3" {
  bucket         = "ai-recipes-terraform-state-YOUR-ACCOUNT-ID"
  key            = "ai-recipes-generator/terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "ai-recipes-terraform-locks"
  encrypt        = true
}
```

### 3. Set Environment Variables

Create a `.env` file or set environment variables:

```bash
export TF_VAR_gemini_api_key="your-gemini-api-key"
export AWS_DEFAULT_REGION="us-east-1"
```

## Deployment

### Staging Environment

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="environments/staging.tfvars"

# Apply deployment
terraform apply -var-file="environments/staging.tfvars"
```

### Production Environment

```bash
# Plan deployment
terraform plan -var-file="environments/production.tfvars"

# Apply deployment
terraform apply -var-file="environments/production.tfvars"
```

## Post-Deployment Steps

### 1. Build and Push Docker Image

```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -t ai-recipes-generator-backend ./backend
docker tag ai-recipes-generator-backend:latest YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/ai-recipes-generator-backend-staging:latest

# Push image
docker push YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/ai-recipes-generator-backend-staging:latest
```

### 2. Deploy Frontend

```bash
# Build frontend
cd frontend
npm install
npm run build

# Upload to S3
aws s3 sync build/ s3://FRONTEND-BUCKET-NAME --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id DISTRIBUTION-ID --paths "/*"
```

### 3. Set Up Database

```bash
# Connect to RDS instance (use bastion host or VPN)
psql -h DATABASE-ENDPOINT -U recipes_user -d recipes_db

# Run database migrations
python backend/manage.py migrate
```

## Monitoring and Maintenance

### View Logs

```bash
# ECS logs
aws logs tail /ecs/ai-recipes-generator-staging --follow

# RDS logs
aws logs describe-log-groups --log-group-name-prefix "/aws/rds"
```

### Scaling

```bash
# Scale ECS service
aws ecs update-service --cluster ai-recipes-generator-cluster-staging --service ai-recipes-generator-backend-service-staging --desired-count 3
```

### Backup and Recovery

```bash
# Create RDS snapshot
aws rds create-db-snapshot --db-instance-identifier ai-recipes-generator-db-staging --db-snapshot-identifier ai-recipes-generator-backup-$(date +%Y%m%d)

# List snapshots
aws rds describe-db-snapshots --db-instance-identifier ai-recipes-generator-db-staging
```

## Troubleshooting

### Common Issues

1. **ECS Tasks Not Starting**
   - Check CloudWatch logs
   - Verify environment variables in Parameter Store
   - Ensure ECR image exists

2. **Database Connection Issues**
   - Verify security group rules
   - Check RDS endpoint
   - Validate database credentials

3. **Frontend Not Loading**
   - Check S3 bucket policy
   - Verify CloudFront distribution
   - Check Route 53 records (if using custom domain)

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster CLUSTER-NAME --services SERVICE-NAME

# Check RDS status
aws rds describe-db-instances --db-instance-identifier DB-INSTANCE-ID

# Check CloudFront distribution
aws cloudfront get-distribution --id DISTRIBUTION-ID
```

## Cleanup

### Destroy Infrastructure

```bash
# Destroy staging
terraform destroy -var-file="environments/staging.tfvars"

# Destroy production
terraform destroy -var-file="environments/production.tfvars"
```

### Manual Cleanup

Some resources may need manual cleanup:

- S3 bucket contents
- ECR repository images
- CloudWatch log groups
- RDS snapshots

## Security Considerations

1. **API Keys**: Store in AWS Parameter Store, never in code
2. **Database**: Use strong passwords, enable encryption
3. **S3**: Block public access, use CloudFront OAC
4. **VPC**: Use private subnets for database and application
5. **SSL**: Use ACM certificates for custom domains

## Cost Optimization

1. **Use Fargate Spot** for non-critical workloads
2. **Enable S3 lifecycle policies**
3. **Use CloudWatch scheduled scaling**
4. **Regular review of unused resources**

## Support

For issues and questions:
1. Check AWS CloudWatch logs
2. Review Terraform plan output
3. Validate AWS resource limits
4. Check service quotas
