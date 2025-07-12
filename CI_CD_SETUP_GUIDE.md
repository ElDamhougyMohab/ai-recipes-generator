# 🚀 CI/CD Pipeline Setup Guide

## Overview
This guide will help you set up comprehensive CI/CD pipelines for your AI Recipes Generator project using GitHub Actions.

## 📋 Prerequisites

### 1. GitHub Repository Setup
- Push your code to a GitHub repository
- Enable GitHub Actions (should be enabled by default)

### 2. Required Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions, and add:

#### Environment Secrets:
```
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Database (Production)
PROD_DATABASE_URL=postgresql://user:password@host:5432/database
PROD_API_URL=https://your-production-api.com

# Database (Staging)
STAGING_DATABASE_URL=postgresql://user:password@staging-host:5432/database
STAGING_API_URL=https://your-staging-api.com

# Database Password
DB_PASSWORD=your_secure_database_password
```

### 3. Environment Setup
Create GitHub Environments:
1. Go to Settings → Environments
2. Create `staging` environment
3. Create `production` environment
4. Add protection rules for production (require reviews)

## 🔧 Pipeline Structure

### 1. **Main CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
**Triggers:** Push to main/develop, Pull requests
**What it does:**
- ✅ Runs backend tests with PostgreSQL
- ✅ Runs frontend tests
- ✅ Generates PDF test reports
- ✅ Security scanning
- ✅ Builds Docker images
- ✅ Deploys to staging/production

### 2. **Comprehensive Testing** (`.github/workflows/test-suite.yml`)
**Triggers:** Push, Pull requests, Daily schedule
**What it does:**
- 🧪 Runs your complete test suite
- 📊 Generates PDF reports
- 🔄 Integration tests with Docker
- 💬 Comments on PRs with test results

### 3. **Security Monitoring** (`.github/workflows/security.yml`)
**Triggers:** Weekly schedule, Dependency changes
**What it does:**
- 🔒 Security audits
- 🔍 Dependency vulnerability checks
- 🐳 Docker image scanning
- 📋 Code quality checks

### 4. **Manual Deployment** (`.github/workflows/deploy.yml`)
**Triggers:** Manual dispatch
**What it does:**
- 🎯 Deploy specific versions to any environment
- 🔄 Environment-specific configurations
- ✅ Health checks after deployment

## 🎯 Key Features

### ✅ **Automated Testing**
- Your 100+ test suite runs automatically
- PDF reports generated and stored as artifacts
- Database testing with PostgreSQL
- Integration testing with Docker

### 🔒 **Security First**
- Vulnerability scanning for dependencies
- Docker image security checks
- Code quality analysis
- Secrets management

### 🚀 **Smart Deployment**
- Environment-specific configurations
- Health checks and rollback capabilities
- Manual approval for production
- Artifact management

### 📊 **Comprehensive Reporting**
- PDF test reports in artifacts
- PR comments with test summaries
- Security scan results
- Build summaries

## 🛠️ Setup Steps

### Step 1: Repository Setup
```bash
# Ensure your repository has the workflow files
git add .github/workflows/
git commit -m "Add CI/CD pipelines"
git push origin main
```

### Step 2: Configure Secrets
Add all required secrets in GitHub repository settings.

### Step 3: Set up Environments
1. Create `staging` and `production` environments
2. Add environment-specific secrets
3. Configure protection rules

### Step 4: Test the Pipeline
```bash
# Create a feature branch
git checkout -b feature/test-cicd

# Make a small change
echo "# Testing CI/CD" >> README.md

# Commit and push
git add README.md
git commit -m "Test CI/CD pipeline"
git push origin feature/test-cicd

# Create a Pull Request
```

## 📁 File Structure
```
.github/
├── workflows/
│   ├── ci-cd.yml          # Main CI/CD pipeline
│   ├── test-suite.yml     # Comprehensive testing
│   ├── security.yml       # Security monitoring
│   └── deploy.yml         # Manual deployment
├── docker-compose.prod.yml # Production Docker setup
├── frontend/
│   ├── Dockerfile.prod    # Production frontend Docker
│   └── nginx.conf         # Nginx configuration
└── backend/
    └── Dockerfile.prod    # Production backend Docker
```

## 🔍 Monitoring and Troubleshooting

### Check Pipeline Status
- Go to Actions tab in your GitHub repository
- View detailed logs for each job
- Download artifacts (PDF reports, etc.)

### Common Issues and Solutions

#### 1. **Database Connection Issues**
```yaml
# Make sure PostgreSQL service is properly configured
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: recipe_pass
      POSTGRES_USER: recipe_user
      POSTGRES_DB: recipes_db_test
```

#### 2. **Secret Not Found**
- Check secret names match exactly
- Verify environment-specific secrets are set
- Ensure secrets are accessible to the workflow

#### 3. **Docker Build Failures**
- Check Dockerfile syntax
- Verify all required files are included
- Review build context

## 🎯 Deployment Options

### Option 1: Self-Hosted
- Deploy to your own servers
- Use SSH actions for deployment
- Manage infrastructure yourself

### Option 2: Cloud Platforms
- **Heroku**: Easy deployment with GitHub integration
- **DigitalOcean**: App Platform or Droplets
- **AWS**: ECS, EKS, or EC2
- **Google Cloud**: Cloud Run or GKE

### Option 3: Container Platforms
- **Railway**: Modern deployment platform
- **Fly.io**: Edge deployment
- **Render**: Simple cloud platform

## 🔄 Workflow Examples

### Automatic on Push:
```
Push to main → Tests → Build → Deploy to Production
Push to develop → Tests → Build → Deploy to Staging
```

### Pull Request:
```
PR Created → Tests → Security Scan → Comment Results
```

### Manual Deployment:
```
Manual Trigger → Select Environment → Deploy → Health Check
```

## 📈 Best Practices

1. **Always test in staging first**
2. **Use environment-specific configurations**
3. **Monitor deployment health**
4. **Keep secrets secure**
5. **Review security scan results**
6. **Use artifacts for debugging**

## 🎉 What's Next?

1. **Set up monitoring**: Add application monitoring
2. **Database migrations**: Implement automatic migrations
3. **Backup strategy**: Set up database backups
4. **Performance monitoring**: Add performance metrics
5. **Alerting**: Set up failure notifications

Your AI Recipes Generator now has enterprise-grade CI/CD pipelines! 🚀
