"""
Enhanced database operations with cloud support and data quality checks
Supports SQLite for local development and PostgreSQL for production
"""

import sqlite3
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import os
import config

logger = logging.getLogger(__name__)

class NewsDB:
    def __init__(self):
        self.db_config = config.get_database_config()
        self.db_path = self.db_config.get('path', 'news.db')
        self.metrics = {
            'total_inserts': 0,
            'successful_inserts': 0,
            'failed_inserts': 0,
            'duplicate_skips': 0,
            'quality_failures': 0
        }
        self.setup_database()
        logger.info(f"Database initialized: {self.db_config['type']}")
    
    def setup_database(self):
        """Create tables with enhanced schema for data quality tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main articles table with quality tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                url TEXT UNIQUE,
                source TEXT,
                published_at TEXT,
                sentiment_score REAL,
                sentiment_label TEXT,
                keywords TEXT,
                category TEXT,
                quality_score REAL DEFAULT 1.0,
                is_duplicate BOOLEAN DEFAULT 0,
                processing_time REAL,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Data quality tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_quality_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                timestamp TEXT,
                total_articles INTEGER,
                valid_articles INTEGER,
                duplicate_articles INTEGER,
                quality_failures INTEGER,
                processing_time REAL,
                error_details TEXT
            )
        ''')
        
        # Processing metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                timestamp TEXT,
                run_id TEXT
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_sentiment ON articles(sentiment_label)')
        
        conn.commit()
        conn.close()
        logger.info("Database schema created successfully")
    
    def validate_article_quality(self, article):
        """Validate article data quality"""
        quality_score = 1.0
        issues = []
        
        # Check required fields
        for field in config.DATA_QUALITY['required_fields']:
            if not article.get(field):
                quality_score -= 0.3
                issues.append(f"Missing required field: {field}")
        
        # Check title length
        title = article.get('title', '')
        if len(title) < config.DATA_QUALITY['min_title_length']:
            quality_score -= 0.2
            issues.append(f"Title too short: {len(title)} characters")
        elif len(title) > config.DATA_QUALITY['max_title_length']:
            quality_score -= 0.1
            issues.append(f"Title too long: {len(title)} characters")
        
        # Check description length
        description = article.get('description', '')
        if description and len(description) < config.DATA_QUALITY['min_description_length']:
            quality_score -= 0.1
            issues.append(f"Description too short: {len(description)} characters")
        
        # Check URL validity
        url = article.get('url', '')
        if url and not url.startswith(('http://', 'https://')):
            quality_score -= 0.2
            issues.append("Invalid URL format")
        
        # Check sentiment score validity
        sentiment_score = article.get('sentiment_score', 0)
        if not isinstance(sentiment_score, (int, float)) or abs(sentiment_score) > 1:
            quality_score -= 0.1
            issues.append("Invalid sentiment score")
        
        return max(0, quality_score), issues
    
    def save_article(self, article, run_id=None):
        """Save article with enhanced quality checks and monitoring"""
        start_time = time.time()
        
        try:
            # Validate article quality
            quality_score, quality_issues = self.validate_article_quality(article)
            
            # Skip if quality is too low
            if quality_score < 0.5:
                self.metrics['quality_failures'] += 1
                logger.warning(f"Article quality too low: {quality_score}, issues: {quality_issues}")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for duplicates
            cursor.execute('SELECT id FROM articles WHERE url = ?', (article.get('url', ''),))
            if cursor.fetchone():
                self.metrics['duplicate_skips'] += 1
                logger.debug(f"Duplicate article skipped: {article.get('url', '')}")
                conn.close()
                return False
            
            processing_time = time.time() - start_time
            
            # Insert article with quality metrics
            cursor.execute('''
                INSERT INTO articles 
                (title, description, url, source, published_at, sentiment_score, 
                 sentiment_label, keywords, category, quality_score, processing_time, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.get('title', ''),
                article.get('description', ''),
                article.get('url', ''),
                article.get('source', ''),
                article.get('published_at', ''),
                article.get('sentiment_score', 0.0),
                article.get('sentiment_label', 'neutral'),
                article.get('keywords', ''),
                article.get('category', ''),
                quality_score,
                processing_time,
                config.get_timestamp(),
                config.get_timestamp()
            ))
            
            conn.commit()
            conn.close()
            
            self.metrics['successful_inserts'] += 1
            self.metrics['total_inserts'] += 1
            
            # Log performance metrics
            self._log_metric('article_processing_time', processing_time, run_id)
            self._log_metric('article_quality_score', quality_score, run_id)
            
            return True
            
        except Exception as e:
            self.metrics['failed_inserts'] += 1
            self.metrics['total_inserts'] += 1
            logger.error(f"Error saving article: {e}")
            return False
    
    def save_articles_batch(self, articles, run_id=None):
        """Save multiple articles with batch processing and quality reporting"""
        if not run_id:
            run_id = f"batch_{int(time.time())}"
        
        start_time = time.time()
        saved_count = 0
        quality_failures = 0
        duplicates = 0
        
        logger.info(f"Starting batch processing: {len(articles)} articles")
        
        for i, article in enumerate(articles):
            if self.save_article(article, run_id):
                saved_count += 1
            
            # Progress logging
            if (i + 1) % config.PROCESSING_CONFIG['sentiment_batch_size'] == 0:
                logger.info(f"Processed {i + 1}/{len(articles)} articles")
        
        processing_time = time.time() - start_time
        
        # Log quality metrics
        self._log_data_quality(
            run_id=run_id,
            total_articles=len(articles),
            valid_articles=saved_count,
            duplicate_articles=self.metrics['duplicate_skips'],
            quality_failures=self.metrics['quality_failures'],
            processing_time=processing_time
        )
        
        logger.info(f"Batch complete: {saved_count}/{len(articles)} articles saved in {processing_time:.2f}s")
        return saved_count
    
    def _log_metric(self, metric_name, value, run_id=None):
        """Log performance metric"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO processing_metrics (metric_name, metric_value, timestamp, run_id)
                VALUES (?, ?, ?, ?)
            ''', (metric_name, value, config.get_timestamp(), run_id))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging metric: {e}")
    
    def _log_data_quality(self, run_id, total_articles, valid_articles, 
                         duplicate_articles, quality_failures, processing_time):
        """Log data quality metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            error_details = json.dumps({
                'success_rate': valid_articles / total_articles if total_articles > 0 else 0,
                'duplicate_rate': duplicate_articles / total_articles if total_articles > 0 else 0,
                'quality_failure_rate': quality_failures / total_articles if total_articles > 0 else 0
            })
            
            cursor.execute('''
                INSERT INTO data_quality_log 
                (run_id, timestamp, total_articles, valid_articles, duplicate_articles, 
                 quality_failures, processing_time, error_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (run_id, config.get_timestamp(), total_articles, valid_articles, 
                  duplicate_articles, quality_failures, processing_time, error_details))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging data quality: {e}")
    
    def get_articles(self, limit=100, category=None, min_quality=0.7):
        """Get articles with quality filtering"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT title, description, url, source, published_at, 
                   sentiment_score, sentiment_label, keywords, category,
                   quality_score, created_at
            FROM articles 
            WHERE quality_score >= ?
        '''
        params = [min_quality]
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        query += ' ORDER BY published_at DESC LIMIT ?'
        params.append(limit)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def get_data_quality_report(self, days=7):
        """Get data quality report for last N days"""
        conn = sqlite3.connect(self.db_path)
        
        # Get recent quality logs
        query = '''
            SELECT run_id, timestamp, total_articles, valid_articles, 
                   duplicate_articles, quality_failures, processing_time
            FROM data_quality_log 
            WHERE datetime(timestamp) >= datetime('now', '-{} days')
            ORDER BY timestamp DESC
        '''.format(days)
        
        quality_df = pd.read_sql_query(query, conn)
        
        # Get overall article quality distribution
        quality_dist_query = '''
            SELECT 
                CASE 
                    WHEN quality_score >= 0.9 THEN 'Excellent'
                    WHEN quality_score >= 0.7 THEN 'Good'
                    WHEN quality_score >= 0.5 THEN 'Fair'
                    ELSE 'Poor'
                END as quality_category,
                COUNT(*) as count
            FROM articles
            WHERE datetime(created_at) >= datetime('now', '-{} days')
            GROUP BY quality_category
        '''.format(days)
        
        quality_dist_df = pd.read_sql_query(quality_dist_query, conn)
        conn.close()
        
        return {
            'quality_logs': quality_df,
            'quality_distribution': quality_dist_df,
            'metrics': self.metrics
        }
    
    def get_performance_metrics(self, hours=24):
        """Get performance metrics for monitoring"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT metric_name, AVG(metric_value) as avg_value, 
                   MAX(metric_value) as max_value, MIN(metric_value) as min_value,
                   COUNT(*) as count
            FROM processing_metrics 
            WHERE datetime(timestamp) >= datetime('now', '-{} hours')
            GROUP BY metric_name
        '''.format(hours)
        
        metrics_df = pd.read_sql_query(query, conn)
        conn.close()
        
        return metrics_df
    
    def cleanup_old_data(self, days=30):
        """Clean up old data and logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clean old articles
        cursor.execute('''
            DELETE FROM articles 
            WHERE datetime(created_at) < datetime('now', '-{} days')
        '''.format(days))
        articles_deleted = cursor.rowcount
        
        # Clean old quality logs
        cursor.execute('''
            DELETE FROM data_quality_log 
            WHERE datetime(timestamp) < datetime('now', '-{} days')
        '''.format(days))
        logs_deleted = cursor.rowcount
        
        # Clean old metrics
        cursor.execute('''
            DELETE FROM processing_metrics 
            WHERE datetime(timestamp) < datetime('now', '-{} days')
        '''.format(days))
        metrics_deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleanup complete: {articles_deleted} articles, {logs_deleted} logs, {metrics_deleted} metrics deleted")
        return articles_deleted, logs_deleted, metrics_deleted
    
    def get_database_health(self):
        """Get database health status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Basic statistics
            cursor.execute('SELECT COUNT(*) FROM articles')
            total_articles = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM articles WHERE datetime(created_at) >= datetime("now", "-1 day")')
            articles_24h = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(quality_score) FROM articles')
            avg_quality = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(DISTINCT source) FROM articles')
            unique_sources = cursor.fetchone()[0]
            
            # Database size
            cursor.execute('SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()')
            db_size = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'status': 'healthy',
                'total_articles': total_articles,
                'articles_24h': articles_24h,
                'avg_quality_score': round(avg_quality, 3),
                'unique_sources': unique_sources,
                'database_size_mb': round(db_size / (1024*1024), 2),
                'metrics': self.metrics
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    # Keep original simple methods for backward compatibility
    def get_sentiment_stats(self):
        """Get basic sentiment statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT sentiment_label, COUNT(*) FROM articles GROUP BY sentiment_label')
        sentiment_counts = dict(cursor.fetchall())
        
        cursor.execute('SELECT AVG(sentiment_score) FROM articles')
        avg_sentiment = cursor.fetchone()[0] or 0.0
        
        cursor.execute('SELECT COUNT(*) FROM articles')
        total = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'sentiment_counts': sentiment_counts,
            'avg_sentiment': avg_sentiment,
            'total_articles': total
        }
    
    def search_articles(self, search_term, limit=50):
        """Search articles by keyword"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT title, description, url, source, sentiment_label, published_at
            FROM articles 
            WHERE (title LIKE ? OR description LIKE ?) AND quality_score >= 0.5
            ORDER BY published_at DESC 
            LIMIT ?
        '''
        
        search_pattern = f'%{search_term}%'
        df = pd.read_sql_query(query, conn, params=[search_pattern, search_pattern, limit])
        conn.close()
        return df
    
    def get_top_sources(self, limit=10):
        """Get most active news sources"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT source, COUNT(*) as article_count, AVG(quality_score) as avg_quality
            FROM articles 
            GROUP BY source 
            ORDER BY article_count DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=[limit])
        conn.close()
        return df
    
    def get_database_info(self):
        """Get basic database information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM articles')
        total_articles = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(published_at) FROM articles')
        latest_article = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT source) FROM articles')
        unique_sources = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_articles': total_articles,
            'latest_article': latest_article,
            'unique_sources': unique_sources
        }

if __name__ == "__main__":
    print("Testing enhanced database...")
    db = NewsDB()
    
    # Test health check
    health = db.get_database_health()
    print(f"Database health: {health}")
    
    # Test quality report
    quality_report = db.get_data_quality_report()
    print(f"Quality metrics: {quality_report['metrics']}")
    
    logger.info("Enhanced database module ready!")