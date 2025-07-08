
import os
import logging
from datetime import datetime, timedelta

# Environment detection
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'

# API Configuration
API_KEY = os.getenv('GNEWS_API_KEY', "your_api")
BASE_URL = "https://gnews.io/api/v4"

# Database Configuration - Cloud Support
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///news.db')
DATABASE_CONFIG = {
    'development': {
        'type': 'sqlite',
        'path': 'news.db',
        'pool_size': 5
    },
    'production': {
        'type': 'postgresql',
        'url': os.getenv('DATABASE_URL', 'sqlite:///news.db'),
        'pool_size': 20,
        'max_overflow': 30
    }
}

# Cloud Storage Configuration
CLOUD_STORAGE = {
    'provider': os.getenv('CLOUD_PROVIDER', 'local'),  # 'aws', 'azure', 'local'
    'aws': {
        'bucket': os.getenv('AWS_S3_BUCKET', 'news-intelligence-data'),
        'region': os.getenv('AWS_REGION', 'us-east-1'),
        'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
        'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY')
    },
    'azure': {
        'storage_account': os.getenv('AZURE_STORAGE_ACCOUNT'),
        'container': os.getenv('AZURE_CONTAINER', 'news-data'),
        'connection_string': os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    }
}

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.getenv('LOG_FILE', 'news_pipeline.log')

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Create logger
logger = logging.getLogger(__name__)

# News Configuration
CATEGORIES = [
    'general', 'world', 'business', 'technology', 
    'entertainment', 'sports', 'science', 'health'
]

SEARCH_TOPICS = [
    "artificial intelligence",
    "climate change", 
    "technology news",
    "business updates",
    "health news",
    "cryptocurrency",
    "space exploration"
]

# Processing Configuration
PROCESSING_CONFIG = {
    'max_articles_per_run': int(os.getenv('MAX_ARTICLES_PER_RUN', '500')),
    'max_articles_per_category': int(os.getenv('MAX_ARTICLES_PER_CATEGORY', '50')),
    'max_articles_per_topic': int(os.getenv('MAX_ARTICLES_PER_TOPIC', '30')),
    'sentiment_batch_size': int(os.getenv('SENTIMENT_BATCH_SIZE', '100')),
    'api_rate_limit': float(os.getenv('API_RATE_LIMIT', '1.0')),  # seconds between calls
    'max_retries': int(os.getenv('MAX_RETRIES', '3')),
    'retry_delay': float(os.getenv('RETRY_DELAY', '2.0'))
}

# Data Quality Configuration
DATA_QUALITY = {
    'min_title_length': int(os.getenv('MIN_TITLE_LENGTH', '10')),
    'max_title_length': int(os.getenv('MAX_TITLE_LENGTH', '200')),
    'min_description_length': int(os.getenv('MIN_DESCRIPTION_LENGTH', '20')),
    'max_description_length': int(os.getenv('MAX_DESCRIPTION_LENGTH', '500')),
    'required_fields': ['title', 'url', 'source'],
    'duplicate_threshold': float(os.getenv('DUPLICATE_THRESHOLD', '0.8'))
}

# Sentiment Analysis Configuration
SENTIMENT_CONFIG = {
    'positive_threshold': float(os.getenv('POSITIVE_THRESHOLD', '0.1')),
    'negative_threshold': float(os.getenv('NEGATIVE_THRESHOLD', '-0.1')),
    'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', '0.5')),
    'max_keywords': int(os.getenv('MAX_KEYWORDS', '10'))
}

# Real-time Processing Configuration
REALTIME_CONFIG = {
    'enabled': os.getenv('REALTIME_ENABLED', 'false').lower() == 'true',
    'interval_minutes': int(os.getenv('REALTIME_INTERVAL', '15')),
    'max_concurrent_requests': int(os.getenv('MAX_CONCURRENT_REQUESTS', '5')),
    'batch_processing': os.getenv('BATCH_PROCESSING', 'true').lower() == 'true'
}

# Dashboard Configuration
DASHBOARD_CONFIG = {
    'title': os.getenv('DASHBOARD_TITLE', 'News Intelligence Pipeline'),
    'host': os.getenv('DASHBOARD_HOST', 'localhost'),
    'port': int(os.getenv('DASHBOARD_PORT', '8501')),
    'auto_refresh': os.getenv('AUTO_REFRESH', 'true').lower() == 'true',
    'refresh_interval': int(os.getenv('REFRESH_INTERVAL', '300')),  # seconds
    'max_articles_display': int(os.getenv('MAX_ARTICLES_DISPLAY', '100'))
}

# Monitoring Configuration
MONITORING = {
    'enabled': os.getenv('MONITORING_ENABLED', 'true').lower() == 'true',
    'metrics_endpoint': os.getenv('METRICS_ENDPOINT', '/metrics'),
    'health_check_endpoint': os.getenv('HEALTH_CHECK_ENDPOINT', '/health'),
    'alert_thresholds': {
        'error_rate': float(os.getenv('ERROR_RATE_THRESHOLD', '0.05')),
        'processing_time': float(os.getenv('PROCESSING_TIME_THRESHOLD', '300')),
        'memory_usage': float(os.getenv('MEMORY_USAGE_THRESHOLD', '0.8'))
    }
}

def get_timestamp():
    """Get current timestamp in standard format"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_yesterday():
    """Get yesterday's date for API calls"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%dT%H:%M:%SZ')

def get_database_config():
    """Get database configuration based on environment"""
    return DATABASE_CONFIG.get(ENVIRONMENT, DATABASE_CONFIG['development'])

def get_cloud_storage_config():
    """Get cloud storage configuration"""
    provider = CLOUD_STORAGE['provider']
    if provider == 'aws':
        return CLOUD_STORAGE['aws']
    elif provider == 'azure':
        return CLOUD_STORAGE['azure']
    else:
        return {'provider': 'local'}

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check required environment variables for production
    if ENVIRONMENT == 'production':
        required_vars = ['GNEWS_API_KEY']
        for var in required_vars:
            if not os.getenv(var):
                errors.append(f"Missing required environment variable: {var}")
    
    # Validate API key
    if not API_KEY or len(API_KEY) < 10:
        errors.append("Invalid or missing API key")
    
    # Validate thresholds
    if SENTIMENT_CONFIG['positive_threshold'] <= SENTIMENT_CONFIG['negative_threshold']:
        errors.append("Positive threshold must be greater than negative threshold")
    
    return errors

def get_performance_config():
    """Get performance-related configuration"""
    return {
        'max_workers': int(os.getenv('MAX_WORKERS', '4')),
        'chunk_size': int(os.getenv('CHUNK_SIZE', '50')),
        'timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
        'connection_pool_size': int(os.getenv('CONNECTION_POOL_SIZE', '10'))
    }

# Application Health Check
def health_check():
    """Basic health check for the application"""
    try:
        # Check database connectivity
        db_status = "healthy"
        
        # Check API availability
        api_status = "healthy" if API_KEY else "unhealthy"
        
        # Check disk space (basic check)
        import shutil
        disk_usage = shutil.disk_usage('/')
        disk_free_gb = disk_usage.free / (1024**3)
        disk_status = "healthy" if disk_free_gb > 1 else "warning"
        
        return {
            'status': 'healthy',
            'timestamp': get_timestamp(),
            'environment': ENVIRONMENT,
            'database': db_status,
            'api': api_status,
            'disk_space_gb': round(disk_free_gb, 2),
            'disk_status': disk_status,
            'version': '1.0.0'
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'timestamp': get_timestamp(),
            'error': str(e)
        }

if __name__ == "__main__":
    print("=== NEWS INTELLIGENCE PIPELINE CONFIGURATION ===")
    print(f"Environment: {ENVIRONMENT}")
    print(f"Debug Mode: {DEBUG}")
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Database: {get_database_config()['type']}")
    print(f"Log Level: {LOG_LEVEL}")
    print(f"Cloud Provider: {CLOUD_STORAGE['provider']}")
    print(f"Real-time Processing: {REALTIME_CONFIG['enabled']}")
    
    # Validate configuration
    config_errors = validate_config()
    if config_errors:
        print(f"\n❌ Configuration Errors:")
        for error in config_errors:
            print(f"  - {error}")
    else:
        print("\n✅ Configuration valid!")
    
    # Show health check
    health = health_check()
    print(f"\n🏥 Health Status: {health['status']}")
    
    logger.info("Configuration loaded successfully")
