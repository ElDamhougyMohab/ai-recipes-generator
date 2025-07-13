@echo off
REM AI Recipes Generator - Terraform Deployment Script (Windows)
REM This script helps deploy the application to AWS using Terraform

setlocal enabledelayedexpansion

REM Function to print colored output
echo [INFO] AI Recipes Generator - Terraform Deployment Script

REM Check if command is provided
if "%1"=="" (
    echo [ERROR] No command provided. Use 'help' for usage information.
    exit /b 1
)

REM Check dependencies
echo [INFO] Checking dependencies...

REM Check AWS CLI
aws --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] AWS CLI is not installed. Please install it first.
    exit /b 1
)

REM Check Terraform
terraform --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Terraform is not installed. Please install it first.
    exit /b 1
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install it first.
    exit /b 1
)

echo [INFO] All dependencies are installed.

REM Check AWS credentials
echo [INFO] Checking AWS credentials...
aws sts get-caller-identity >nul 2>&1
if errorlevel 1 (
    echo [ERROR] AWS credentials are not configured. Please run 'aws configure' first.
    exit /b 1
)

REM Get AWS Account ID
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo [INFO] AWS Account ID: %ACCOUNT_ID%

REM Main command processing
if "%1"=="deploy" (
    if "%2"=="" (
        echo [ERROR] Environment not specified. Use 'staging' or 'production'.
        exit /b 1
    )
    
    if not "%2"=="staging" if not "%2"=="production" (
        echo [ERROR] Invalid environment. Use 'staging' or 'production'.
        exit /b 1
    )
    
    call :deploy %2
    goto :end
)

if "%1"=="destroy" (
    if "%2"=="" (
        echo [ERROR] Environment not specified. Use 'staging' or 'production'.
        exit /b 1
    )
    
    call :destroy %2
    goto :end
)

if "%1"=="help" (
    call :show_help
    goto :end
)

echo [ERROR] Invalid command. Use 'help' for usage information.
exit /b 1

:deploy
set ENV=%1
echo [INFO] Starting deployment for %ENV% environment...

REM Setup Terraform backend
call :setup_backend

REM Check Gemini API key
if "%TF_VAR_gemini_api_key%"=="" (
    echo [WARNING] Gemini API key not found in environment variables.
    set /p "GEMINI_API_KEY=Please enter your Gemini API key: "
    set TF_VAR_gemini_api_key=!GEMINI_API_KEY!
)

echo [INFO] Initializing Terraform...
terraform init
if errorlevel 1 exit /b 1

echo [INFO] Validating Terraform configuration...
terraform validate
if errorlevel 1 exit /b 1

echo [INFO] Planning deployment for %ENV% environment...
terraform plan -var-file="environments/%ENV%.tfvars" -out="%ENV%.tfplan"
if errorlevel 1 exit /b 1

set /p "CONFIRM=Do you want to apply the deployment? (y/N): "
if /i "%CONFIRM%"=="y" (
    echo [INFO] Applying deployment for %ENV% environment...
    terraform apply "%ENV%.tfplan"
    if errorlevel 1 exit /b 1
    
    call :build_and_push_image %ENV%
    call :deploy_frontend
    call :show_deployment_summary
    
    echo [INFO] Deployment completed successfully!
) else (
    echo [INFO] Deployment cancelled.
)
goto :eof

:destroy
set ENV=%1
echo [WARNING] This will destroy all resources in the %ENV% environment.
set /p "CONFIRM=Are you sure you want to continue? (y/N): "
if /i "%CONFIRM%"=="y" (
    terraform destroy -var-file="environments/%ENV%.tfvars"
    echo [INFO] Infrastructure destroyed successfully!
) else (
    echo [INFO] Destruction cancelled.
)
goto :eof

:setup_backend
echo [INFO] Setting up Terraform backend...
set BUCKET_NAME=ai-recipes-terraform-state-%ACCOUNT_ID%
set TABLE_NAME=ai-recipes-terraform-locks

REM Check if S3 bucket exists
aws s3 ls "s3://%BUCKET_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Creating S3 bucket: %BUCKET_NAME%
    aws s3 mb "s3://%BUCKET_NAME%"
    
    REM Enable versioning
    aws s3api put-bucket-versioning --bucket "%BUCKET_NAME%" --versioning-configuration Status=Enabled
    
    REM Enable encryption
    aws s3api put-bucket-encryption --bucket "%BUCKET_NAME%" --server-side-encryption-configuration "{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"AES256\"}}]}"
) else (
    echo [INFO] S3 bucket already exists: %BUCKET_NAME%
)

REM Check if DynamoDB table exists
aws dynamodb describe-table --table-name "%TABLE_NAME%" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Creating DynamoDB table: %TABLE_NAME%
    aws dynamodb create-table --table-name "%TABLE_NAME%" --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
    
    echo [INFO] Waiting for DynamoDB table to be created...
    aws dynamodb wait table-exists --table-name "%TABLE_NAME%"
) else (
    echo [INFO] DynamoDB table already exists: %TABLE_NAME%
)

REM Update main.tf with correct backend configuration
echo [INFO] Updating backend configuration...
powershell -Command "(gc main.tf) -replace 'bucket = \".*\"', 'bucket = \"%BUCKET_NAME%\"' | Out-File -encoding ASCII main.tf"
powershell -Command "(gc main.tf) -replace 'dynamodb_table = \".*\"', 'dynamodb_table = \"%TABLE_NAME%\"' | Out-File -encoding ASCII main.tf"
goto :eof

:build_and_push_image
echo [INFO] Building and pushing Docker image...

REM Get ECR repository URL
for /f "tokens=*" %%i in ('terraform output -raw ecr_repository_url') do set ECR_REPO=%%i

REM Get ECR login token
for /f "tokens=*" %%i in ('aws ecr get-login-password --region us-east-1') do docker login --username AWS --password-stdin %ECR_REPO% <nul

REM Build image
echo [INFO] Building Docker image...
docker build -t ai-recipes-generator-backend ../backend
if errorlevel 1 exit /b 1

REM Tag image
docker tag ai-recipes-generator-backend:latest "%ECR_REPO%:latest"
if errorlevel 1 exit /b 1

REM Push image
echo [INFO] Pushing Docker image to ECR...
docker push "%ECR_REPO%:latest"
if errorlevel 1 exit /b 1

echo [INFO] Docker image pushed successfully!
goto :eof

:deploy_frontend
echo [INFO] Deploying frontend...

REM Get S3 bucket name and CloudFront distribution ID
for /f "tokens=*" %%i in ('terraform output -raw frontend_bucket_name') do set BUCKET_NAME=%%i
for /f "tokens=*" %%i in ('terraform output -raw cloudfront_distribution_id') do set DISTRIBUTION_ID=%%i

REM Build frontend
echo [INFO] Building frontend...
cd ../frontend
call npm install
if errorlevel 1 exit /b 1
call npm run build
if errorlevel 1 exit /b 1

REM Upload to S3
echo [INFO] Uploading frontend to S3...
aws s3 sync build/ "s3://%BUCKET_NAME%" --delete
if errorlevel 1 exit /b 1

REM Invalidate CloudFront cache
echo [INFO] Invalidating CloudFront cache...
aws cloudfront create-invalidation --distribution-id "%DISTRIBUTION_ID%" --paths "/*"
if errorlevel 1 exit /b 1

cd ../terraform
echo [INFO] Frontend deployed successfully!
goto :eof

:show_deployment_summary
echo [INFO] Deployment Summary:
echo ====================

for /f "tokens=*" %%i in ('terraform output -raw frontend_url 2^>nul') do (
    if not "%%i"=="" echo Frontend URL: %%i
)

for /f "tokens=*" %%i in ('terraform output -raw api_url 2^>nul') do (
    if not "%%i"=="" echo API URL: %%i
)

for /f "tokens=*" %%i in ('terraform output -raw database_endpoint 2^>nul') do (
    if not "%%i"=="" echo Database Endpoint: %%i
)

echo ====================
goto :eof

:show_help
echo AI Recipes Generator - Terraform Deployment Script
echo.
echo Usage: %~nx0 ^<command^> [environment]
echo.
echo Commands:
echo   deploy ^<staging^|production^>   - Deploy infrastructure and application
echo   destroy ^<staging^|production^>  - Destroy infrastructure
echo   help                          - Show this help message
echo.
echo Examples:
echo   %~nx0 deploy staging
echo   %~nx0 deploy production
echo   %~nx0 destroy staging
echo.
echo Prerequisites:
echo   - AWS CLI configured with appropriate credentials
echo   - Terraform installed
echo   - Docker installed
echo   - Node.js and npm installed
echo   - GEMINI_API_KEY environment variable set
goto :eof

:end
endlocal
