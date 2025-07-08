"""
Enhanced data ingestion with real-time processing, monitoring, and cloud support
Includes retry logic, concurrent processing, and performance monitoring
"""

import requests
import time
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import threading
from dataclasses import dataclass
import config

logger = logging.getLogger(__name__)

@dataclass
class IngestionMetrics:
    """Track ingestion performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_articles: int = 0
    processing_time: float = 0.0
    rate_limit_hits: int = 0
    retries_attempted: int = 0
    
    def success_rate(self) -> float:
        return (self.successful_requests / self.total_requests) if self.total_requests > 0 else 0.0
    
    def articles_per_second(self) -> float:
        return (self.total_articles / self.processing_time) if self.processing_time > 0 else 0.0

class NewsFetcher:
    def __init__(self):
        self.api_key = config.API_KEY
        self.base_url = config.BASE_URL
        self.metrics = IngestionMetrics()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NewsIntelligence/1.0 (Professional Data Pipeline)',
            'Accept': 'application/json',
            'Connection': 'keep-alive'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.rate_limit_lock = threading.Lock()
        
        # Real-time processing
        self.realtime_enabled = config.REALTIME_CONFIG['enabled']
        self.realtime_interval = config.REALTIME_CONFIG['interval_minutes']
        self.realtime_running = False
        
        logger.info(f"News fetcher initialized - Real-time: {self.realtime_enabled}")
    
    def _enforce_rate_limit(self):
        """Enforce API rate limiting with thread safety"""
        with self.rate_limit_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < config.PROCESSING_CONFIG['api_rate_limit']:
                sleep_time = config.PROCESSING_CONFIG['api_rate_limit'] - time_since_last
                time.sleep(sleep_time)
                self.metrics.rate_limit_hits += 1
            
            self.last_request_time = time.time()
    
    def _make_request_with_retry(self, url: str, params: Dict[str, Any], 
                               max_retries: int = None) -> Optional[Dict[str, Any]]:
        """Make HTTP request with retry logic and monitoring"""
        if max_retries is None:
            max_retries = config.PROCESSING_CONFIG['max_retries']
        
        self._enforce_rate_limit()
        
        # Add API key to parameters
        params['apikey'] = self.api_key
        
        for attempt in range(max_retries + 1):
            try:
                self.metrics.total_requests += 1
                
                logger.debug(f"API Request (attempt {attempt + 1}): {url}")
                logger.debug(f"Parameters: {params}")
                
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=config.get_performance_config()['timeout']
                )
                response.raise_for_status()
                
                data = response.json()
                self.metrics.successful_requests += 1
                
                # Log response metrics
                total_articles = data.get('totalArticles', 0)
                articles_returned = len(data.get('articles', []))
                
                logger.info(f"API Success: {articles_returned} articles returned (total available: {total_articles})")
                
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{max_retries + 1})")
                if attempt < max_retries:
                    self.metrics.retries_attempted += 1
                    time.sleep(config.PROCESSING_CONFIG['retry_delay'] * (attempt + 1))
                    continue
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    logger.warning(f"Rate limit hit (attempt {attempt + 1}/{max_retries + 1})")
                    if attempt < max_retries:
                        self.metrics.retries_attempted += 1
                        time.sleep(config.PROCESSING_CONFIG['retry_delay'] * (attempt + 1) * 2)
                        continue
                else:
                    logger.error(f"HTTP Error {e.response.status_code}: {e}")
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < max_retries:
                    self.metrics.retries_attempted += 1
                    time.sleep(config.PROCESSING_CONFIG['retry_delay'] * (attempt + 1))
                    continue
                    
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break
        
        self.metrics.failed_requests += 1
        return None
    
    def fetch_headlines(self, category='general', max_articles=50):
        """Get top headlines from a category with enhanced error handling"""
        url = f"{self.base_url}/top-headlines"
        
        params = {
            'category': category,
            'lang': 'en',
            'country': 'us',
            'max': min(max_articles, config.PROCESSING_CONFIG['max_articles_per_category'])
        }
        
        start_time = time.time()
        response = self._make_request_with_retry(url, params)
        processing_time = time.time() - start_time
        
        if not response:
            return []
        
        articles = response.get('articles', [])
        processed_articles = []
        
        for article in articles:
            processed = self._process_article(article, category)
            if processed:
                processed_articles.append(processed)
        
        self.metrics.total_articles += len(processed_articles)
        self.metrics.processing_time += processing_time
        
        logger.info(f"Fetched {len(processed_articles)} articles from {category} in {processing_time:.2f}s")
        return processed_articles
    
    def search_news(self, query, max_articles=30):
        """Search for news with enhanced monitoring"""
        url = f"{self.base_url}/search"
        
        params = {
            'q': query,
            'lang': 'en',
            'country': 'us',
            'max': min(max_articles, config.PROCESSING_CONFIG['max_articles_per_topic']),
            'sortby': 'publishedAt'
        }
        
        start_time = time.time()
        response = self._make_request_with_retry(url, params)
        processing_time = time.time() - start_time
        
        if not response:
            return []
        
        articles = response.get('articles', [])
        processed_articles = []
        
        for article in articles:
            processed = self._process_article(article, 'search')
            if processed:
                processed_articles.append(processed)
        
        self.metrics.total_articles += len(processed_articles)
        self.metrics.processing_time += processing_time
        
        logger.info(f"Found {len(processed_articles)} articles for '{query}' in {processing_time:.2f}s")
        return processed_articles
    
    def _process_article(self, article, category):
        """Process article with enhanced validation and monitoring"""
        try:
            source_info = article.get('source', {})
            
            # Enhanced validation
            if not article.get('title'):
                logger.debug("Skipping article: missing title")
                return None
            
            if not article.get('url'):
                logger.debug("Skipping article: missing URL")
                return None
            
            # Process published date with better handling
            published_at = article.get('publishedAt', '')
            if published_at:
                try:
                    dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    published_at = dt.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    logger.warning(f"Invalid date format: {published_at}")
                    published_at = config.get_timestamp()
            else:
                published_at = config.get_timestamp()
            
            processed = {
                'title': article.get('title', '').strip()[:config.DATA_QUALITY['max_title_length']],
                'description': article.get('description', '').strip()[:config.DATA_QUALITY['max_description_length']],
                'url': article.get('url', '').strip(),
                'source': source_info.get('name', 'Unknown').strip(),
                'published_at': published_at,
                'category': category,
                'image_url': article.get('image', ''),
                'fetch_timestamp': config.get_timestamp(),
                'api_response_time': time.time()
            }
            
            # Additional validation
            if len(processed['title']) < config.DATA_QUALITY['min_title_length']:
                logger.debug(f"Skipping article: title too short ({len(processed['title'])} chars)")
                return None
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return None
    
    def fetch_concurrent_categories(self, categories=None, max_articles_per_category=20):
        """Fetch multiple categories concurrently for better performance"""
        if categories is None:
            categories = config.CATEGORIES
        
        logger.info(f"Starting concurrent fetch for {len(categories)} categories")
        start_time = time.time()
        
        all_articles = []
        
        with ThreadPoolExecutor(max_workers=config.get_performance_config()['max_workers']) as executor:
            # Submit all category fetches
            future_to_category = {
                executor.submit(self.fetch_headlines, category, max_articles_per_category): category
                for category in categories
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_category):
                category = future_to_category[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                    logger.info(f"Completed fetch for category: {category} ({len(articles)} articles)")
                except Exception as e:
                    logger.error(f"Error fetching category {category}: {e}")
        
        total_time = time.time() - start_time
        logger.info(f"Concurrent fetch complete: {len(all_articles)} articles in {total_time:.2f}s")
        
        return all_articles
    
    def search_concurrent_topics(self, topics=None, max_articles_per_topic=25):
        """Search multiple topics concurrently"""
        if topics is None:
            topics = config.SEARCH_TOPICS
        
        logger.info(f"Starting concurrent search for {len(topics)} topics")
        start_time = time.time()
        
        all_articles = []
        
        with ThreadPoolExecutor(max_workers=config.get_performance_config()['max_workers']) as executor:
            # Submit all topic searches
            future_to_topic = {
                executor.submit(self.search_news, topic, max_articles_per_topic): topic
                for topic in topics
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_topic):
                topic = future_to_topic[future]
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                    logger.info(f"Completed search for topic: {topic} ({len(articles)} articles)")
                except Exception as e:
                    logger.error(f"Error searching topic {topic}: {e}")
        
        # Remove duplicates
        unique_articles = self._remove_duplicates(all_articles)
        
        total_time = time.time() - start_time
        logger.info(f"Concurrent search complete: {len(unique_articles)} unique articles in {total_time:.2f}s")
        
        return unique_articles
    
    def _remove_duplicates(self, articles):
        """Remove duplicate articles efficiently"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        duplicates_removed = len(articles) - len(unique_articles)
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate articles")
        
        return unique_articles
    
    def run_full_fetch(self, run_id=None):
        """Enhanced full fetch with performance monitoring"""
        if not run_id:
            run_id = f"full_fetch_{int(time.time())}"
        
        logger.info(f"Starting full news fetch (run_id: {run_id})")
        start_time = time.time()
        
        # Reset metrics for this run
        self.metrics = IngestionMetrics()
        
        try:
            # Concurrent category fetch
            logger.info("Phase 1: Fetching category headlines...")
            category_articles = self.fetch_concurrent_categories(
                max_articles_per_category=config.PROCESSING_CONFIG['max_articles_per_category']
            )
            
            # Concurrent topic search
            logger.info("Phase 2: Searching trending topics...")
            search_articles = self.search_concurrent_topics(
                max_articles_per_topic=config.PROCESSING_CONFIG['max_articles_per_topic']
            )
            
            # Combine and deduplicate
            logger.info("Phase 3: Combining and deduplicating...")
            all_articles = category_articles + search_articles
            unique_articles = self._remove_duplicates(all_articles)
            
            # Apply article limit
            max_articles = config.PROCESSING_CONFIG['max_articles_per_run']
            if len(unique_articles) > max_articles:
                unique_articles = unique_articles[:max_articles]
                logger.info(f"Limited to {max_articles} articles")
            
            total_time = time.time() - start_time
            self.metrics.processing_time = total_time
            
            # Log comprehensive metrics
            logger.info(f"Full fetch complete (run_id: {run_id})")
            logger.info(f"  Total articles: {len(unique_articles)}")
            logger.info(f"  Processing time: {total_time:.2f}s")
            logger.info(f"  Success rate: {self.metrics.success_rate():.2%}")
            logger.info(f"  Articles/second: {self.metrics.articles_per_second():.2f}")
            logger.info(f"  API requests: {self.metrics.total_requests}")
            logger.info(f"  Retries: {self.metrics.retries_attempted}")
            
            return unique_articles
            
        except Exception as e:
            logger.error(f"Full fetch failed (run_id: {run_id}): {e}")
            return []
    
    def start_realtime_processing(self, callback=None):
        """Start real-time news processing"""
        if not self.realtime_enabled:
            logger.info("Real-time processing is disabled")
            return
        
        if self.realtime_running:
            logger.warning("Real-time processing already running")
            return
        
        self.realtime_running = True
        logger.info(f"Starting real-time processing (interval: {self.realtime_interval} minutes)")
        
        def realtime_loop():
            while self.realtime_running:
                try:
                    logger.info("Real-time fetch triggered")
                    articles = self.run_full_fetch(run_id=f"realtime_{int(time.time())}")
                    
                    if callback and articles:
                        callback(articles)
                    
                    # Sleep for the specified interval
                    sleep_time = self.realtime_interval * 60
                    for _ in range(sleep_time):
                        if not self.realtime_running:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Real-time processing error: {e}")
                    time.sleep(60)  # Wait 1 minute before retry
        
        # Start real-time processing in a separate thread
        thread = threading.Thread(target=realtime_loop, daemon=True)
        thread.start()
        
        return thread
    
    def stop_realtime_processing(self):
        """Stop real-time news processing"""
        if self.realtime_running:
            self.realtime_running = False
            logger.info("Real-time processing stopped")
    
    def get_ingestion_metrics(self):
        """Get current ingestion metrics"""
        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'success_rate': self.metrics.success_rate(),
            'total_articles': self.metrics.total_articles,
            'processing_time': self.metrics.processing_time,
            'articles_per_second': self.metrics.articles_per_second(),
            'rate_limit_hits': self.metrics.rate_limit_hits,
            'retries_attempted': self.metrics.retries_attempted,
            'realtime_enabled': self.realtime_enabled,
            'realtime_running': self.realtime_running
        }
    
    def get_health_status(self):
        """Get ingestion health status"""
        try:
            # Test API connection
            test_response = self._make_request_with_retry(
                f"{self.base_url}/search",
                {'q': 'test', 'max': 1}
            )
            
            api_status = 'healthy' if test_response else 'unhealthy'
            
            return {
                'status': api_status,
                'api_key_valid': bool(self.api_key and len(self.api_key) > 10),
                'rate_limit_active': self.metrics.rate_limit_hits > 0,
                'metrics': self.get_ingestion_metrics()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def test_connection(self):
        """Test API connection with detailed diagnostics"""
        logger.info("Testing API connection...")
        
        try:
            # Test basic connectivity
            test_articles = self.search_news('test', 1)
            
            if test_articles:
                logger.info("✅ API connection successful")
                logger.info(f"✅ Sample article: {test_articles[0]['title']}")
                return True
            else:
                logger.warning("⚠️ API connection failed - no articles returned")
                return False
                
        except Exception as e:
            logger.error(f"❌ API connection failed: {e}")
            return False

# Async version for advanced real-time processing
class AsyncNewsFetcher:
    """Async version of news fetcher for high-performance real-time processing"""
    
    def __init__(self):
        self.api_key = config.API_KEY
        self.base_url = config.BASE_URL
        self.semaphore = asyncio.Semaphore(config.REALTIME_CONFIG['max_concurrent_requests'])
        logger.info("Async news fetcher initialized")
    
    async def fetch_with_session(self, session, url, params):
        """Fetch single URL with async session"""
        async with self.semaphore:
            try:
                params['apikey'] = self.api_key
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                logger.error(f"Async fetch error: {e}")
                return None
    
    async def fetch_all_async(self, requests_list):
        """Fetch multiple requests concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url, params in requests_list:
                task = self.fetch_with_session(session, url, params)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return [r for r in results if r is not None and not isinstance(r, Exception)]

if __name__ == "__main__":
    print("Testing enhanced news fetcher...")
    fetcher = NewsFetcher()
    
    # Test connection
    if fetcher.test_connection():
        print("\n🔍 Testing enhanced fetch...")
        articles = fetcher.run_full_fetch()
        
        if articles:
            print(f"Fetched {len(articles)} articles")
            print(f"Sample: {articles[0]['title']}")
        
        # Show metrics
        metrics = fetcher.get_ingestion_metrics()
        print(f"\n📊 Metrics:")
        print(f"  Success rate: {metrics['success_rate']:.2%}")
        print(f"  Articles/second: {metrics['articles_per_second']:.2f}")
        print(f"  API requests: {metrics['total_requests']}")
        
        # Test health status
        health = fetcher.get_health_status()
        print(f"\n🏥 Health: {health['status']}")
    
    logger.info("Enhanced news fetcher ready!")