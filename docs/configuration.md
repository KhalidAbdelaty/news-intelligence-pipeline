# ⚙️ Configuration Reference

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GNEWS_API_KEY` | GNews API authentication key | `86ce66a3c06ea6a6a4a6fa14e290f092` |

### Core Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment name (development/production) |
| `DEBUG` | `true` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `LOG_FILE` | `news_pipeline.log` | Log file path |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///news.db` | Database connection string |
| `DATABASE_PATH` | `news.db` | SQLite database file path |

**PostgreSQL Example:**
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/news_db"
```

### API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_ARTICLES_PER_RUN` | `500` | Maximum articles per pipeline run |
| `MAX_ARTICLES_PER_CATEGORY` | `50` | Maximum articles per category |
| `MAX_ARTICLES_PER_TOPIC` | `30` | Maximum articles per search topic |
| `API_RATE_LIMIT` | `1.0` | Seconds between API calls |
| `MAX_RETRIES` | `3` | Maximum API retry attempts |
| `RETRY_DELAY` | `2.0` | Delay between retries (seconds) |

### Processing Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTIMENT_BATCH_SIZE` | `100` | Articles per processing batch |
| `MIN_TITLE_LENGTH` | `10` | Minimum title length |
| `MAX_TITLE_LENGTH` | `200` | Maximum title length |
| `MIN_DESCRIPTION_LENGTH` | `20` | Minimum description length |
| `MAX_DESCRIPTION_LENGTH` | `500` | Maximum description length |
| `POSITIVE_THRESHOLD` | `0.1` | Positive sentiment threshold |
| `NEGATIVE_THRESHOLD` | `-0.1` | Negative sentiment threshold |
| `CONFIDENCE_THRESHOLD` | `0.5` | Minimum confidence for sentiment |
| `MAX_KEYWORDS` | `10` | Maximum keywords per article |

### Real-time Processing

| Variable | Default | Description |
|----------|---------|-------------|
| `REALTIME_ENABLED` | `false` | Enable real-time processing |
| `REALTIME_INTERVAL` | `15` | Minutes between real-time runs |
| `MAX_CONCURRENT_REQUESTS` | `5` | Maximum concurrent API requests |
| `BATCH_PROCESSING` | `true` | Enable batch processing mode |

### Dashboard Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DASHBOARD_TITLE` | `News Intelligence Pipeline` | Dashboard title |
| `DASHBOARD_HOST` | `localhost` | Dashboard host |
| `DASHBOARD_PORT` | `8501` | Dashboard port |
| `AUTO_REFRESH` | `true` | Enable auto-refresh |
| `REFRESH_INTERVAL` | `300` | Auto-refresh interval (seconds) |
| `MAX_ARTICLES_DISPLAY` | `100` | Maximum articles in dashboard |

### Cloud Storage (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `CLOUD_PROVIDER` | `local` | Cloud provider (aws/azure/local) |
| `AWS_S3_BUCKET` | `news-intelligence-data` | AWS S3 bucket name |
| `AWS_REGION` | `us-east-1` | AWS region |
| `AWS_ACCESS_KEY_ID` | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | - | AWS secret key |
| `AZURE_STORAGE_ACCOUNT` | - | Azure storage account |
| `AZURE_CONTAINER` | `news-data` | Azure container name |
| `AZURE_STORAGE_CONNECTION_STRING` | - | Azure connection string |

### Monitoring Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MONITORING_ENABLED` | `true` | Enable monitoring |
| `METRICS_ENDPOINT` | `/metrics` | Metrics endpoint path |
| `HEALTH_CHECK_ENDPOINT` | `/health` | Health check endpoint |
| `ERROR_RATE_THRESHOLD` | `0.05` | Alert threshold for error rate |
| `PROCESSING_TIME_THRESHOLD` | `300` | Alert threshold for processing time |
| `MEMORY_USAGE_THRESHOLD` | `0.8` | Alert threshold for memory usage |

### Performance Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_WORKERS` | `4` | Maximum worker threads |
| `CHUNK_SIZE` | `50` | Processing chunk size |
| `REQUEST_TIMEOUT` | `30` | HTTP request timeout (seconds) |
| `CONNECTION_POOL_SIZE` | `10` | Database connection pool size |

## Configuration Files

### .env File Example
```bash
# API Configuration
GNEWS_API_KEY=86ce66a3c06ea6a6a4a6fa14e290f092
ENVIRONMENT=production

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/news_db

# Processing
MAX_ARTICLES_PER_RUN=1000
REALTIME_ENABLED=true
REALTIME_INTERVAL=10

# Dashboard
DASHBOARD_PORT=8501
AUTO_REFRESH=true

# Monitoring
LOG_LEVEL=INFO
MONITORING_ENABLED=true

# Cloud (Optional)
CLOUD_PROVIDER=aws
AWS_S3_BUCKET=my-news-bucket
AWS_REGION=us-west-2
```

### Docker Environment
```yaml
# docker-compose.yml
environment:
  - GNEWS_API_KEY=${GNEWS_API_KEY}
  - ENVIRONMENT=production
  - DATABASE_PATH=/app/data/news.db
  - LOG_LEVEL=INFO
  - REALTIME_ENABLED=true
  - MAX_ARTICLES_PER_RUN=500
```

## Configuration Validation

The system automatically validates configuration on startup:

### Required Validation
- API key presence and format
- Database connectivity
- File system permissions

### Warning Validation
- Performance settings optimization
- Memory allocation
- Disk space availability

### Configuration Functions

```python
# Check configuration
from config import validate_config, health_check

# Validate all settings
errors = validate_config()
if errors:
    print("Configuration errors:", errors)

# Health check
status = health_check()
print("System status:", status['status'])
```

## Environment-Specific Settings

### Development
```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///news_dev.db
MAX_ARTICLES_PER_RUN=100
REALTIME_ENABLED=false
```

### Production
```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@prod-db:5432/news
MAX_ARTICLES_PER_RUN=1000
REALTIME_ENABLED=true
MONITORING_ENABLED=true
```

### Testing
```bash
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///:memory:
MAX_ARTICLES_PER_RUN=10
REALTIME_ENABLED=false
```

## Security Considerations

### API Keys
- Never commit API keys to version control
- Use environment variables or secure vaults
- Rotate keys regularly

### Database
- Use strong passwords
- Enable SSL connections in production
- Restrict network access

### Monitoring
- Limit access to metrics endpoints
- Sanitize logs to remove sensitive data
- Enable audit logging

## Performance Tuning

### High Volume Processing
```bash
MAX_ARTICLES_PER_RUN=2000
SENTIMENT_BATCH_SIZE=200
MAX_WORKERS=8
CONNECTION_POOL_SIZE=20
```

### Low Resource Environment
```bash
MAX_ARTICLES_PER_RUN=100
SENTIMENT_BATCH_SIZE=25
MAX_WORKERS=2
CONNECTION_POOL_SIZE=5
```

### Real-time Optimization
```bash
REALTIME_ENABLED=true
REALTIME_INTERVAL=5
MAX_CONCURRENT_REQUESTS=10
BATCH_PROCESSING=true
```
