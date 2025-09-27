# 🚀 Support Solutions CRM - CI/CD Pipeline

This document explains the CI/CD setup for the Support Solutions CRM system.

## 🔄 Pipeline Overview

Our CI/CD pipeline runs automatically on:
- **Push to `main`** → Deploy to Production
- **Push to `develop`** → Deploy to Staging  
- **Pull Requests** → Run tests and quality checks

## 🧪 Pipeline Stages

### 1. **Test & Quality Checks** 🧪
- **Code Formatting**: Black, isort
- **Linting**: Flake8 
- **Security Scanning**: Bandit, Safety
- **Unit Tests**: pytest with coverage
- **Import Tests**: Verify all modules load

### 2. **Build Application** 🏗️
- **Dependency Installation**
- **Module Import Testing**
- **Database Connection Testing**

### 3. **Security Scan** 🛡️
- **CodeQL Analysis**: GitHub's semantic code analysis
- **Vulnerability Detection**
- **Dependency Security Check**

### 4. **Deployment** 🚀
- **Staging**: Auto-deploy from `develop` branch
- **Production**: Auto-deploy from `main` branch

## 🔧 Setup Instructions

### 1. **GitHub Secrets Configuration**
Add these secrets in your GitHub repository settings:

```
OPENAI_API_KEY          # Your OpenAI API key for AI functionality
RAILWAY_TOKEN           # Railway deployment token (optional)
```

### 2. **Local Development Testing**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
flake8 .
black --check .
isort --check-only .

# Run security checks
bandit -r .
safety check
```

### 3. **Branch Strategy**
- `main` → Production environment
- `develop` → Staging environment  
- Feature branches → Create PR to `develop`

## 🌐 Deployment Platforms

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway up
```

### Docker Deployment
```bash
# Build image
docker build -t support-solutions-crm .

# Run container
docker run -p 5001:5001 -e OPENAI_API_KEY=your_key support-solutions-crm
```

### Manual Deployment
```bash
# Setup production environment
pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key
python web.py
```

## 📊 Monitoring & Health Checks

- **Health Endpoint**: `/api/status`
- **Coverage Reports**: Automatically uploaded to Codecov
- **Build Status**: Visible in GitHub Actions tab
- **Security Alerts**: GitHub Security tab

## 🔒 Security Features

- **Dependency Scanning**: Automated vulnerability detection
- **Code Analysis**: Static analysis for security issues
- **Container Security**: Non-root user in Docker
- **Input Validation**: XSS and SQL injection protection

## 🚀 Deployment URLs

- **Production**: `https://support-solutions.railway.app`
- **Staging**: `https://support-solutions-staging.railway.app`
- **Health Check**: `https://your-app.railway.app/api/status`

## 📈 Pipeline Benefits

✅ **Automated Testing** - Catch bugs before deployment  
✅ **Code Quality** - Enforce consistent formatting and standards  
✅ **Security** - Scan for vulnerabilities automatically  
✅ **Fast Deployment** - Push to deploy in minutes  
✅ **Rollback Ready** - Easy to revert problematic deployments  
✅ **Monitoring** - Health checks and status monitoring  

## 🛠️ Customization

### Adding New Tests
Add tests to `tests/test_crm_system.py` or create new test files in the `tests/` directory.

### Modifying Pipeline
Edit `.github/workflows/ci-cd.yml` to customize the pipeline behavior.

### Environment Variables
Configure additional environment variables in your deployment platform or GitHub secrets.

---

**Happy Deploying! 🚀**