#!/bin/bash

# AI Recipes Generator - Terraform Deployment Script
# This script helps deploy the application to AWS using Terraform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    print_status "All dependencies are installed."
}

# Function to check AWS credentials
check_aws_credentials() {
    print_status "Checking AWS credentials..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    print_status "AWS Account ID: $ACCOUNT_ID"
}

# Function to create S3 bucket for Terraform state
create_terraform_backend() {
    print_status "Setting up Terraform backend..."
    
    BUCKET_NAME="ai-recipes-terraform-state-${ACCOUNT_ID}"
    TABLE_NAME="ai-recipes-terraform-locks"
    
    # Create S3 bucket
    if aws s3 ls "s3://${BUCKET_NAME}" 2>&1 | grep -q 'NoSuchBucket'; then
        print_status "Creating S3 bucket: ${BUCKET_NAME}"
        aws s3 mb "s3://${BUCKET_NAME}"
        
        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket "${BUCKET_NAME}" \
            --versioning-configuration Status=Enabled
        
        # Enable server-side encryption
        aws s3api put-bucket-encryption \
            --bucket "${BUCKET_NAME}" \
            --server-side-encryption-configuration '{
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }'
    else
        print_status "S3 bucket already exists: ${BUCKET_NAME}"
    fi
    
    # Create DynamoDB table for state locking
    if ! aws dynamodb describe-table --table-name "${TABLE_NAME}" &> /dev/null; then
        print_status "Creating DynamoDB table: ${TABLE_NAME}"
        aws dynamodb create-table \
            --table-name "${TABLE_NAME}" \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
        
        # Wait for table to be created
        print_status "Waiting for DynamoDB table to be created..."
        aws dynamodb wait table-exists --table-name "${TABLE_NAME}"
    else
        print_status "DynamoDB table already exists: ${TABLE_NAME}"
    fi
    
    # Update main.tf with correct backend configuration
    print_status "Updating backend configuration..."
    sed -i.bak "s/bucket = \".*\"/bucket = \"${BUCKET_NAME}\"/" main.tf
    sed -i.bak "s/dynamodb_table = \".*\"/dynamodb_table = \"${TABLE_NAME}\"/" main.tf
}

# Function to check if Gemini API key is set
check_gemini_api_key() {
    print_status "Checking Gemini API key..."
    
    if [ -z "${TF_VAR_gemini_api_key}" ]; then
        print_warning "Gemini API key not found in environment variables."
        read -p "Please enter your Gemini API key: " -s GEMINI_API_KEY
        echo
        export TF_VAR_gemini_api_key="${GEMINI_API_KEY}"
    fi
    
    print_status "Gemini API key is set."
}

# Function to initialize Terraform
terraform_init() {
    print_status "Initializing Terraform..."
    terraform init
}

# Function to validate Terraform configuration
terraform_validate() {
    print_status "Validating Terraform configuration..."
    terraform validate
}

# Function to plan deployment
terraform_plan() {
    local environment=$1
    
    print_status "Planning deployment for ${environment} environment..."
    terraform plan -var-file="environments/${environment}.tfvars" -out="${environment}.tfplan"
}

# Function to apply deployment
terraform_apply() {
    local environment=$1
    
    print_status "Applying deployment for ${environment} environment..."
    terraform apply "${environment}.tfplan"
}

# Function to build and push Docker image
build_and_push_image() {
    local environment=$1
    
    print_status "Building and pushing Docker image..."
    
    # Get ECR repository URL
    ECR_REPO=$(terraform output -raw ecr_repository_url)
    
    # Get ECR login token
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "${ECR_REPO}"
    
    # Build image
    print_status "Building Docker image..."
    docker build -t ai-recipes-generator-backend ../backend
    
    # Tag image
    docker tag ai-recipes-generator-backend:latest "${ECR_REPO}:latest"
    
    # Push image
    print_status "Pushing Docker image to ECR..."
    docker push "${ECR_REPO}:latest"
    
    print_status "Docker image pushed successfully!"
}

# Function to deploy frontend
deploy_frontend() {
    print_status "Deploying frontend..."
    
    # Get S3 bucket name and CloudFront distribution ID
    BUCKET_NAME=$(terraform output -raw frontend_bucket_name)
    DISTRIBUTION_ID=$(terraform output -raw cloudfront_distribution_id)
    
    # Build frontend
    print_status "Building frontend..."
    cd ../frontend
    npm install
    npm run build
    
    # Upload to S3
    print_status "Uploading frontend to S3..."
    aws s3 sync build/ "s3://${BUCKET_NAME}" --delete
    
    # Invalidate CloudFront cache
    print_status "Invalidating CloudFront cache..."
    aws cloudfront create-invalidation --distribution-id "${DISTRIBUTION_ID}" --paths "/*"
    
    cd ../terraform
    print_status "Frontend deployed successfully!"
}

# Function to show deployment summary
show_deployment_summary() {
    print_status "Deployment Summary:"
    echo "===================="
    
    if terraform output frontend_url &> /dev/null; then
        echo "Frontend URL: $(terraform output -raw frontend_url)"
    fi
    
    if terraform output api_url &> /dev/null; then
        echo "API URL: $(terraform output -raw api_url)"
    fi
    
    if terraform output database_endpoint &> /dev/null; then
        echo "Database Endpoint: $(terraform output -raw database_endpoint)"
    fi
    
    echo "===================="
}

# Main deployment function
deploy() {
    local environment=$1
    
    if [ -z "$environment" ]; then
        print_error "Environment not specified. Use 'staging' or 'production'."
        exit 1
    fi
    
    if [ "$environment" != "staging" ] && [ "$environment" != "production" ]; then
        print_error "Invalid environment. Use 'staging' or 'production'."
        exit 1
    fi
    
    print_status "Starting deployment for ${environment} environment..."
    
    check_dependencies
    check_aws_credentials
    create_terraform_backend
    check_gemini_api_key
    terraform_init
    terraform_validate
    terraform_plan "$environment"
    
    # Ask for confirmation
    read -p "Do you want to apply the deployment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform_apply "$environment"
        build_and_push_image "$environment"
        deploy_frontend
        show_deployment_summary
        print_status "Deployment completed successfully!"
    else
        print_status "Deployment cancelled."
    fi
}

# Function to destroy infrastructure
destroy() {
    local environment=$1
    
    if [ -z "$environment" ]; then
        print_error "Environment not specified. Use 'staging' or 'production'."
        exit 1
    fi
    
    print_warning "This will destroy all resources in the ${environment} environment."
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform destroy -var-file="environments/${environment}.tfvars"
        print_status "Infrastructure destroyed successfully!"
    else
        print_status "Destruction cancelled."
    fi
}

# Function to show help
show_help() {
    echo "AI Recipes Generator - Terraform Deployment Script"
    echo ""
    echo "Usage: $0 <command> [environment]"
    echo ""
    echo "Commands:"
    echo "  deploy <staging|production>   - Deploy infrastructure and application"
    echo "  destroy <staging|production>  - Destroy infrastructure"
    echo "  help                          - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy staging"
    echo "  $0 deploy production"
    echo "  $0 destroy staging"
    echo ""
    echo "Prerequisites:"
    echo "  - AWS CLI configured with appropriate credentials"
    echo "  - Terraform installed"
    echo "  - Docker installed"
    echo "  - Node.js and npm installed"
    echo "  - GEMINI_API_KEY environment variable set"
}

# Main script logic
case "$1" in
    deploy)
        deploy "$2"
        ;;
    destroy)
        destroy "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Invalid command. Use 'help' for usage information."
        exit 1
        ;;
esac
