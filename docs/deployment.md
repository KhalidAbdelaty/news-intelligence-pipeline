# 🚀 Deployment Guide

## AWS Deployment

### AWS App Runner (Easiest)
1. Go to AWS App Runner console
2. Create service → Connect to source code
3. Select GitHub repository
4. Configure:
   - Runtime: Python 3.11
   - Build command: `pip install -r requirements.txt`
   - Start command: `streamlit run dashboard.py --server.headless true --server.port 8501`
5. Environment variables:
   - `GNEWS_API_KEY`: your_api_key
   - `ENVIRONMENT`: production
6. Deploy

### AWS ECS Fargate
```bash
# Build and push to ECR
aws ecr create-repository --repository-name news-intelligence
docker build -t news-intelligence .
docker tag news-intelligence:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/news-intelligence:latest
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/news-intelligence:latest

# Create ECS service
aws ecs create-cluster --cluster-name news-intelligence
# Use provided task definition
```

### AWS Lambda + API Gateway
```bash
# For serverless deployment
pip install zappa
zappa init
zappa deploy production
```

## Azure Deployment

### Azure Container Instances
```bash
az group create --name news-intelligence --location eastus

az container create \
  --resource-group news-intelligence \
  --name news-pipeline \
  --image news-intelligence:latest \
  --cpu 1 --memory 2 \
  --environment-variables GNEWS_API_KEY=your_key ENVIRONMENT=production \
  --ports 8501 \
  --ip-address public
```

### Azure App Service
```bash
az webapp create \
  --resource-group news-intelligence \
  --plan news-plan \
  --name news-intelligence-app \
  --deployment-container-image-name news-intelligence:latest
```

## Google Cloud Platform

### Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/news-intelligence
gcloud run deploy --image gcr.io/PROJECT_ID/news-intelligence --platform managed
```

## Railway Deployment

1. Connect GitHub repository to Railway
2. Set environment variables:
   - `GNEWS_API_KEY`: your_api_key
   - `ENVIRONMENT`: production
3. Deploy automatically on git push

## Environment Variables

### Required
- `GNEWS_API_KEY`: Your GNews API key

### Optional
- `ENVIRONMENT`: development/production
- `DATABASE_URL`: PostgreSQL connection string
- `LOG_LEVEL`: INFO/DEBUG/WARNING
- `MAX_ARTICLES_PER_RUN`: 500
- `REALTIME_ENABLED`: true/false

## Health Checks

All deployments support health checks at:
- `/_stcore/health` - Streamlit health
- Custom health endpoint in dashboard

## SSL/HTTPS

Most cloud platforms provide automatic SSL. For custom domains:
- AWS: Use CloudFront + Certificate Manager
- Azure: Use Application Gateway
- GCP: Use Load Balancer with managed certificates

## Monitoring

### Application Monitoring
- Built-in metrics dashboard
- Performance tracking
- Error logging
- Quality monitoring

### Infrastructure Monitoring
- AWS CloudWatch
- Azure Monitor
- GCP Operations Suite

## Scaling

### Horizontal Scaling
- Load balancer + multiple containers
- Database read replicas
- CDN for static assets

### Vertical Scaling
- Increase CPU/memory
- Optimize database queries
- Enable caching

## Security

### API Security
- Environment variables for secrets
- HTTPS enforcement
- Rate limiting

### Network Security
- VPC/subnet configuration
- Security groups
- Private databases

## Backup & Recovery

### Database Backup
- Automated daily backups
- Point-in-time recovery
- Cross-region replication

### Application Backup
- Source code in Git
- Container images in registry
- Configuration in infrastructure as code
