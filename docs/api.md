# 📚 API Reference

## Overview

The News Intelligence Pipeline provides internal APIs for health monitoring, metrics, and data access.

## Health Endpoints

### Application Health
```
GET /_stcore/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

### Custom Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "healthy",
  "api": "healthy",
  "disk_space_gb": 45.2,
  "version": "1.0.0"
}
```

## Database Operations

### NewsDB Class

#### `save_article(article: Dict) -> bool`
Save a single article to database.

**Parameters:**
- `article`: Dictionary containing article data

**Returns:** Boolean indicating success

**Example:**
```python
from storage import NewsDB
db = NewsDB()

article = {
    'title': 'Breaking News',
    'description': 'Important update',
    'url': 'https://example.com/news',
    'source': 'News Source',
    'published_at': '2025-01-01 12:00:00',
    'sentiment_score': 0.5,
    'sentiment_label': 'positive'
}

success = db.save_article(article)
```

#### `get_articles(limit: int = 100, category: str = None) -> pd.DataFrame`
Retrieve articles from database.

**Parameters:**
- `limit`: Maximum number of articles
- `category`: Filter by category (optional)

**Returns:** Pandas DataFrame with articles

#### `get_sentiment_stats() -> Dict`
Get sentiment analysis statistics.

**Returns:**
```json
{
  "sentiment_counts": {
    "positive": 150,
    "neutral": 200,
    "negative": 50
  },
  "avg_sentiment": 0.15,
  "total_articles": 400
}
```

## Data Processing

### NewsProcessor Class

#### `analyze_sentiment(text: str) -> Tuple[float, str, float]`
Analyze sentiment of text.

**Parameters:**
- `text`: Text to analyze

**Returns:** Tuple of (score, label, confidence)

**Example:**
```python
from transform import NewsProcessor
processor = NewsProcessor()

score, label, confidence = processor.analyze_sentiment("Great news today!")
# Returns: (0.8, 'positive', 0.9)
```

#### `extract_keywords(text: str, max_keywords: int = 10) -> List[str]`
Extract keywords from text.

**Parameters:**
- `text`: Input text
- `max_keywords`: Maximum keywords to return

**Returns:** List of keywords

#### `process_articles_batch(articles: List[Dict]) -> List[Dict]`
Process multiple articles.

**Parameters:**
- `articles`: List of article dictionaries

**Returns:** List of processed articles with sentiment, keywords, categories

## Data Ingestion

### NewsFetcher Class

#### `search_news(query: str, max_articles: int = 30) -> List[Dict]`
Search for news articles.

**Parameters:**
- `query`: Search query
- `max_articles`: Maximum articles to fetch

**Returns:** List of article dictionaries

#### `get_top_headlines(category: str = 'general', max_articles: int = 50) -> List[Dict]`
Get top headlines by category.

**Parameters:**
- `category`: News category
- `max_articles`: Maximum articles to fetch

**Returns:** List of article dictionaries

#### `run_full_fetch(run_id: str = None) -> List[Dict]`
Run complete news ingestion.

**Parameters:**
- `run_id`: Optional run identifier

**Returns:** List of processed articles

## Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GNEWS_API_KEY` | string | required | GNews API key |
| `ENVIRONMENT` | string | development | Environment name |
| `DATABASE_URL` | string | sqlite:///news.db | Database connection |
| `LOG_LEVEL` | string | INFO | Logging level |
| `MAX_ARTICLES_PER_RUN` | int | 500 | Max articles per run |
| `REALTIME_ENABLED` | bool | false | Enable real-time processing |

### Configuration Functions

#### `validate_config() -> List[str]`
Validate configuration settings.

**Returns:** List of validation errors

#### `get_database_config() -> Dict`
Get database configuration for current environment.

#### `health_check() -> Dict`
Perform application health check.

## Error Handling

### Standard Error Response
```json
{
  "error": "Error message",
  "timestamp": "2025-01-01T12:00:00Z",
  "component": "ingestion|processing|storage|dashboard"
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `API_ERROR` | GNews API failure |
| `DB_ERROR` | Database operation failed |
| `PROCESSING_ERROR` | Article processing failed |
| `INVALID_RESPONSE` | Invalid API response |

## Rate Limiting

- **GNews API**: 1 request per second (built-in)
- **Processing**: 100 articles per batch
- **Database**: Connection pooling with limits

## Data Models

### Article Schema
```json
{
  "id": "integer",
  "title": "string (required)",
  "description": "string",
  "url": "string (required, unique)",
  "source": "string (required)",
  "published_at": "datetime",
  "sentiment_score": "float (-1 to 1)",
  "sentiment_label": "string (positive|neutral|negative)",
  "keywords": "string (comma-separated)",
  "category": "string",
  "quality_score": "float (0 to 1)",
  "created_at": "datetime"
}
```

### Quality Metrics Schema
```json
{
  "run_id": "string",
  "timestamp": "datetime",
  "total_articles": "integer",
  "valid_articles": "integer",
  "duplicate_articles": "integer",
  "quality_failures": "integer",
  "processing_time": "float"
}
```

## Usage Examples

### Complete Pipeline Run
```python
from ingest import NewsFetcher
from transform import NewsProcessor
from storage import NewsDB

# Initialize components
fetcher = NewsFetcher()
processor = NewsProcessor()
db = NewsDB()

# Run pipeline
articles = fetcher.run_full_fetch()
processed = processor.process_articles_batch(articles)
saved_count = db.save_articles_batch(processed)

print(f"Saved {saved_count} articles")
```

### Real-time Processing
```python
from ingest import NewsFetcher

fetcher = NewsFetcher()

def process_callback(articles):
    print(f"Processing {len(articles)} articles")

# Start real-time processing
fetcher.start_realtime_processing(callback=process_callback)
```
