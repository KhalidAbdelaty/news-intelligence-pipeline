"""
Enhanced data transformation with advanced analytics and quality monitoring
Includes batch processing, performance optimization, and comprehensive reporting
"""

import re
import time
import threading
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import logging
import json

from textblob import TextBlob
import config

logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    """Track processing performance and quality metrics"""
    total_processed: int = 0
    successful_processed: int = 0
    failed_processed: int = 0
    quality_passed: int = 0
    quality_failed: int = 0
    processing_time: float = 0.0
    sentiment_analysis_time: float = 0.0
    keyword_extraction_time: float = 0.0
    
    def success_rate(self) -> float:
        return (self.successful_processed / self.total_processed) if self.total_processed > 0 else 0.0
    
    def quality_rate(self) -> float:
        return (self.quality_passed / self.total_processed) if self.total_processed > 0 else 0.0
    
    def articles_per_second(self) -> float:
        return (self.total_processed / self.processing_time) if self.processing_time > 0 else 0.0

class NewsProcessor:
    def __init__(self):
        # Enhanced stop words with domain-specific terms
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we', 'our', 'you',
            'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them',
            'their', 'what', 'which', 'who', 'where', 'when', 'why', 'how', 'all',
            'any', 'both', 'each', 'more', 'most', 'other', 'some', 'such', 'no',
            'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'said',
            'says', 'get', 'go', 'make', 'take', 'come', 'see', 'know', 'think',
            'look', 'first', 'last', 'long', 'good', 'new', 'old', 'right', 'big',
            'small', 'different', 'large', 'great', 'little', 'high', 'next', 'early',
            'young', 'important', 'public', 'bad', 'able', 'may', 'might', 'must',
            'can', 'well', 'way', 'even', 'back', 'still', 'just', 'now', 'also',
            'here', 'there', 'up', 'out', 'down', 'over', 'under', 'again', 'off',
            'away', 'around', 'between', 'through', 'during', 'before', 'after',
            'above', 'below', 'into', 'from', 'against', 'about', 'without', 'within',
            # News-specific stop words
            'news', 'report', 'reports', 'according', 'sources', 'source', 'today',
            'yesterday', 'announced', 'breaking', 'update', 'updates', 'latest',
            'story', 'article', 'published', 'writes', 'reports', 'coverage'
        }
        
        # Category detection patterns
        self.category_patterns = {
            'technology': [
                r'\b(ai|artificial intelligence|machine learning|tech|technology|software|app|digital|cyber|data|cloud|blockchain|cryptocurrency|bitcoin|startup|innovation|silicon valley)\b',
                r'\b(google|apple|microsoft|amazon|facebook|meta|tesla|netflix|uber|airbnb|twitter|instagram|tiktok|zoom|slack)\b',
                r'\b(iphone|android|ios|windows|mac|linux|website|internet|online|platform|algorithm|programming|coding)\b'
            ],
            'business': [
                r'\b(business|economy|economic|market|markets|stock|stocks|finance|financial|investment|investor|revenue|profit|earnings|sales|company|corporate|ceo|executive)\b',
                r'\b(wall street|nasdaq|dow jones|sp500|trading|merger|acquisition|ipo|bankruptcy|recession|inflation|gdp|unemployment)\b',
                r'\b(startup|entrepreneur|venture capital|private equity|funding|valuation|unicorn|acquisition|merger)\b'
            ],
            'health': [
                r'\b(health|medical|medicine|doctor|hospital|patient|disease|virus|vaccine|treatment|drug|pharmaceutical|healthcare|wellness|fitness)\b',
                r'\b(covid|coronavirus|pandemic|epidemic|outbreak|symptoms|diagnosis|therapy|surgery|clinic|research|study)\b',
                r'\b(fda|cdc|who|pfizer|moderna|johnson|mental health|depression|anxiety|diabetes|cancer|heart)\b'
            ],
            'sports': [
                r'\b(sports|sport|game|games|team|teams|player|players|coach|championship|tournament|league|season|match|competition)\b',
                r'\b(football|basketball|baseball|soccer|tennis|golf|hockey|olympics|nfl|nba|mlb|fifa|espn|athlete|athletic)\b',
                r'\b(super bowl|world cup|playoffs|finals|draft|trade|injury|score|win|loss|defeat|victory)\b'
            ],
            'entertainment': [
                r'\b(entertainment|movie|movies|film|films|actor|actress|celebrity|music|album|song|concert|show|tv|television|series|streaming)\b',
                r'\b(hollywood|netflix|disney|warner|universal|paramount|oscar|emmy|grammy|box office|premiere|trailer)\b',
                r'\b(director|producer|singer|musician|band|artist|performance|review|rating|cinema|theater)\b'
            ],
            'science': [
                r'\b(science|scientific|research|study|discovery|experiment|climate|environment|space|nasa|physics|chemistry|biology|geology)\b',
                r'\b(climate change|global warming|renewable energy|solar|wind|fossil fuel|carbon|emission|pollution|conservation)\b',
                r'\b(mars|moon|satellite|telescope|spacecraft|asteroid|planet|galaxy|universe|scientist|laboratory)\b'
            ],
            'politics': [
                r'\b(politics|political|government|president|congress|senate|house|election|vote|voting|campaign|politician|policy|law|legislation)\b',
                r'\b(republican|democrat|conservative|liberal|biden|trump|white house|supreme court|justice|governor|mayor)\b',
                r'\b(immigration|healthcare|taxes|budget|deficit|foreign policy|domestic|international|diplomacy|treaty)\b'
            ]
        }
        
        self.metrics = ProcessingMetrics()
        self.processing_lock = threading.Lock()
        
        logger.info("Enhanced news processor initialized")
    
    def clean_text(self, text: str) -> str:
        """Advanced text cleaning with multiple passes"""
        if not text:
            return ""
        
        # Remove HTML tags and entities
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
        
        # Remove URLs and email addresses
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove social media handles and hashtags
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remove multiple spaces, tabs, and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep essential punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\:\;\-\(\)\[\]\'\"]', '', text)
        
        # Remove extra whitespace around punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s+', r'\1 ', text)
        
        # Remove quotes around single words
        text = re.sub(r'\"(\w+)\"', r'\1', text)
        
        return text.strip()
    
    def analyze_sentiment_advanced(self, text: str) -> Tuple[float, str, float]:
        """Advanced sentiment analysis with confidence scoring"""
        if not text:
            return 0.0, 'neutral', 0.0
        
        start_time = time.time()
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Calculate confidence based on subjectivity and polarity magnitude
            confidence = min(1.0, abs(polarity) + (subjectivity * 0.5))
            
            # Enhanced classification with confidence thresholds
            if confidence < config.SENTIMENT_CONFIG['confidence_threshold']:
                label = 'neutral'
                polarity = 0.0  # Normalize low-confidence predictions
            elif polarity > config.SENTIMENT_CONFIG['positive_threshold']:
                label = 'positive'
            elif polarity < config.SENTIMENT_CONFIG['negative_threshold']:
                label = 'negative'
            else:
                label = 'neutral'
            
            self.metrics.sentiment_analysis_time += time.time() - start_time
            return round(polarity, 3), label, round(confidence, 3)
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return 0.0, 'neutral', 0.0
    
    def extract_keywords_advanced(self, text: str, max_keywords: int = None) -> List[str]:
        """Advanced keyword extraction with TF-IDF-like scoring"""
        if not text:
            return []
        
        if max_keywords is None:
            max_keywords = config.SENTIMENT_CONFIG['max_keywords']
        
        start_time = time.time()
        
        try:
            # Clean and tokenize
            cleaned_text = self.clean_text(text.lower())
            
            # Extract words with length filter
            words = re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_text)
            
            # Remove stop words and common terms
            meaningful_words = [
                word for word in words 
                if word not in self.stop_words and len(word) > 2
            ]
            
            # Calculate word frequencies
            word_freq = Counter(meaningful_words)
            
            # Apply simple TF-IDF-like scoring
            # Boost longer words and penalize very common words
            scored_words = []
            total_words = len(meaningful_words)
            
            for word, freq in word_freq.items():
                # Term frequency
                tf = freq / total_words
                
                # Length bonus (longer words are often more meaningful)
                length_bonus = min(2.0, len(word) / 5.0)
                
                # Position bonus (words at beginning might be more important)
                position_bonus = 1.0
                try:
                    first_occurrence = meaningful_words.index(word)
                    position_bonus = max(0.5, 1.0 - (first_occurrence / len(meaningful_words)))
                except ValueError:
                    pass
                
                # Combined score
                score = tf * length_bonus * position_bonus
                scored_words.append((word, score))
            
            # Sort by score and return top keywords
            scored_words.sort(key=lambda x: x[1], reverse=True)
            keywords = [word for word, score in scored_words[:max_keywords]]
            
            self.metrics.keyword_extraction_time += time.time() - start_time
            return keywords
            
        except Exception as e:
            logger.error(f"Keyword extraction error: {e}")
            return []
    
    def categorize_article_advanced(self, article: Dict[str, Any]) -> Tuple[str, float]:
        """Advanced article categorization with confidence scoring"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        
        # Combine title and description with title getting higher weight
        text_to_analyze = f"{title} {title} {description}"  # Title appears twice for weight
        
        category_scores = {}
        
        # Score each category using regex patterns
        for category, patterns in self.category_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_to_analyze, re.IGNORECASE)
                score += len(matches)
            
            # Normalize score by text length
            if len(text_to_analyze) > 0:
                category_scores[category] = score / (len(text_to_analyze.split()) / 100)
            else:
                category_scores[category] = 0
        
        # Find best category
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category]
            
            # If confidence is too low, use existing category or default
            if confidence < 0.1:
                existing_category = article.get('category', 'general')
                if existing_category in config.CATEGORIES:
                    return existing_category, 0.5
                return 'general', 0.3
            
            return best_category, min(1.0, confidence)
        
        return 'general', 0.3
    
    def validate_article_quality(self, article: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """Comprehensive article quality validation"""
        quality_score = 1.0
        issues = []
        
        # Check required fields
        for field in config.DATA_QUALITY['required_fields']:
            if not article.get(field):
                quality_score -= 0.4
                issues.append(f"Missing required field: {field}")
        
        # Title validation
        title = article.get('title', '')
        if not title:
            quality_score -= 0.3
            issues.append("Missing title")
        else:
            if len(title) < config.DATA_QUALITY['min_title_length']:
                quality_score -= 0.2
                issues.append(f"Title too short: {len(title)} characters")
            elif len(title) > config.DATA_QUALITY['max_title_length']:
                quality_score -= 0.1
                issues.append(f"Title too long: {len(title)} characters")
            
            # Check for spam-like titles
            if title.upper() == title and len(title) > 20:
                quality_score -= 0.2
                issues.append("Title is all uppercase")
            
            # Check for excessive punctuation
            punctuation_ratio = sum(1 for char in title if char in '!?.,;:') / len(title)
            if punctuation_ratio > 0.15:
                quality_score -= 0.1
                issues.append("Excessive punctuation in title")
        
        # Description validation
        description = article.get('description', '')
        if description:
            if len(description) < config.DATA_QUALITY['min_description_length']:
                quality_score -= 0.1
                issues.append(f"Description too short: {len(description)} characters")
            elif len(description) > config.DATA_QUALITY['max_description_length']:
                quality_score -= 0.05
                issues.append(f"Description too long: {len(description)} characters")
        
        # URL validation
        url = article.get('url', '')
        if url:
            if not re.match(r'^https?://', url):
                quality_score -= 0.2
                issues.append("Invalid URL format")
        
        # Source validation
        source = article.get('source', '')
        if not source or source.lower() in ['unknown', 'null', 'none']:
            quality_score -= 0.1
            issues.append("Missing or invalid source")
        
        # Content duplication check (basic)
        if title and description:
            title_words = set(title.lower().split())
            desc_words = set(description.lower().split())
            if title_words and len(title_words.intersection(desc_words)) / len(title_words) > 0.8:
                quality_score -= 0.1
                issues.append("High similarity between title and description")
        
        # Date validation
        published_at = article.get('published_at', '')
        if published_at:
            try:
                pub_date = datetime.strptime(published_at, '%Y-%m-%d %H:%M:%S')
                # Check if date is too far in the future
                if pub_date > datetime.now() + timedelta(days=1):
                    quality_score -= 0.1
                    issues.append("Publication date in future")
                # Check if date is too old (more than 1 year)
                elif pub_date < datetime.now() - timedelta(days=365):
                    quality_score -= 0.05
                    issues.append("Article is very old")
            except ValueError:
                quality_score -= 0.05
                issues.append("Invalid date format")
        
        quality_score = max(0, quality_score)
        is_valid = quality_score >= 0.5
        
        return is_valid, quality_score, issues
    
    def detect_trending_topics(self, articles: List[Dict[str, Any]], 
                              time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """Advanced trending topic detection with temporal analysis"""
        try:
            # Group articles by time periods
            time_buckets = defaultdict(list)
            current_time = datetime.now()
            
            for article in articles:
                try:
                    pub_date = datetime.strptime(article.get('published_at', ''), '%Y-%m-%d %H:%M:%S')
                    hours_ago = (current_time - pub_date).total_seconds() / 3600
                    
                    if hours_ago <= time_window_hours:
                        # Bucket by hour
                        hour_bucket = int(hours_ago)
                        time_buckets[hour_bucket].append(article)
                except (ValueError, TypeError):
                    continue
            
            # Analyze keyword trends across time buckets
            keyword_trends = defaultdict(lambda: {'counts': [], 'sentiments': [], 'sources': set()})
            
            for hour, hour_articles in time_buckets.items():
                hour_keywords = defaultdict(int)
                hour_keyword_sentiments = defaultdict(list)
                
                for article in hour_articles:
                    keywords = article.get('keywords', '').split(', ')
                    sentiment = article.get('sentiment_score', 0)
                    source = article.get('source', '')
                    
                    for keyword in keywords:
                        if keyword.strip():
                            keyword = keyword.strip().lower()
                            hour_keywords[keyword] += 1
                            hour_keyword_sentiments[keyword].append(sentiment)
                            keyword_trends[keyword]['sources'].add(source)
                
                # Store hourly data
                for keyword, count in hour_keywords.items():
                    keyword_trends[keyword]['counts'].append((hour, count))
                    avg_sentiment = sum(hour_keyword_sentiments[keyword]) / len(hour_keyword_sentiments[keyword])
                    keyword_trends[keyword]['sentiments'].append(avg_sentiment)
            
            # Calculate trending scores
            trending_topics = []
            for keyword, data in keyword_trends.items():
                if len(data['counts']) < 2:  # Need at least 2 time periods
                    continue
                
                # Calculate trend velocity (increase in mentions over time)
                counts = [count for hour, count in data['counts']]
                if len(counts) >= 2:
                    recent_avg = sum(counts[:len(counts)//2]) / max(1, len(counts)//2)
                    older_avg = sum(counts[len(counts)//2:]) / max(1, len(counts) - len(counts)//2)
                    trend_velocity = recent_avg - older_avg
                else:
                    trend_velocity = 0
                
                # Calculate total mentions
                total_mentions = sum(counts)
                
                # Calculate sentiment consistency
                sentiments = data['sentiments']
                sentiment_std = 0
                if len(sentiments) > 1:
                    avg_sentiment = sum(sentiments) / len(sentiments)
                    sentiment_std = (sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)) ** 0.5
                
                # Calculate diversity (number of sources)
                source_diversity = len(data['sources'])
                
                # Combined trending score
                trending_score = (
                    total_mentions * 0.4 +
                    trend_velocity * 0.3 +
                    source_diversity * 0.2 +
                    (1 - sentiment_std) * 0.1  # More consistent sentiment = higher score
                )
                
                trending_topics.append({
                    'keyword': keyword,
                    'total_mentions': total_mentions,
                    'trend_velocity': round(trend_velocity, 2),
                    'source_diversity': source_diversity,
                    'avg_sentiment': round(sum(sentiments) / len(sentiments), 3) if sentiments else 0,
                    'sentiment_consistency': round(1 - sentiment_std, 3),
                    'trending_score': round(trending_score, 2),
                    'time_periods': len(data['counts'])
                })
            
            # Sort by trending score and return top topics
            trending_topics.sort(key=lambda x: x['trending_score'], reverse=True)
            return trending_topics[:20]
            
        except Exception as e:
            logger.error(f"Error detecting trending topics: {e}")
            return []
    
    def process_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process single article with comprehensive analysis"""
        start_time = time.time()
        
        try:
            with self.processing_lock:
                self.metrics.total_processed += 1
            
            # Validate article quality first
            is_valid, quality_score, quality_issues = self.validate_article_quality(article)
            
            if not is_valid:
                with self.processing_lock:
                    self.metrics.quality_failed += 1
                logger.debug(f"Article failed quality check: {quality_issues}")
                return None
            
            # Extract text for analysis
            title = article.get('title', '')
            description = article.get('description', '')
            text_to_analyze = f"{title} {description}"
            
            # Sentiment analysis
            sentiment_score, sentiment_label, confidence = self.analyze_sentiment_advanced(text_to_analyze)
            
            # Keyword extraction
            keywords = self.extract_keywords_advanced(text_to_analyze)
            
            # Category classification
            category, category_confidence = self.categorize_article_advanced(article)
            
            # Calculate readability score (simple version)
            readability_score = self._calculate_readability(text_to_analyze)
            
            # Create enhanced article
            enhanced_article = article.copy()
            enhanced_article.update({
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'sentiment_confidence': confidence,
                'keywords': ', '.join(keywords),
                'category': category,
                'category_confidence': category_confidence,
                'quality_score': quality_score,
                'readability_score': readability_score,
                'processing_timestamp': config.get_timestamp(),
                'processing_time': round(time.time() - start_time, 4)
            })
            
            # Clean text fields
            enhanced_article['title'] = self.clean_text(title)
            enhanced_article['description'] = self.clean_text(description)
            
            with self.processing_lock:
                self.metrics.successful_processed += 1
                self.metrics.quality_passed += 1
            
            return enhanced_article
            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            with self.processing_lock:
                self.metrics.failed_processed += 1
            return None
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate simple readability score"""
        if not text:
            return 0.0
        
        try:
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return 0.0
            
            words = text.split()
            avg_sentence_length = len(words) / len(sentences)
            
            # Simple readability score (lower is better)
            # Based on average sentence length and word complexity
            long_words = sum(1 for word in words if len(word) > 6)
            long_word_ratio = long_words / len(words) if words else 0
            
            readability = max(0, min(1, 1 - (avg_sentence_length / 25) - (long_word_ratio * 0.5)))
            return round(readability, 3)
            
        except Exception as e:
            logger.error(f"Readability calculation error: {e}")
            return 0.5
    
    def process_articles_batch(self, articles: List[Dict[str, Any]], 
                              batch_size: int = None) -> List[Dict[str, Any]]:
        """Process articles in batches with parallel processing"""
        if not articles:
            return []
        
        if batch_size is None:
            batch_size = config.PROCESSING_CONFIG['sentiment_batch_size']
        
        start_time = time.time()
        self.metrics = ProcessingMetrics()  # Reset metrics for new batch
        
        logger.info(f"Starting batch processing: {len(articles)} articles")
        
        processed_articles = []
        
        # Process in chunks for better memory management
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            
            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=config.get_performance_config()['max_workers']) as executor:
                # Submit all articles in batch
                future_to_article = {
                    executor.submit(self.process_article, article): article
                    for article in batch
                }
                
                # Collect results
                for future in future_to_article:
                    try:
                        result = future.result()
                        if result:
                            processed_articles.append(result)
                    except Exception as e:
                        logger.error(f"Batch processing error: {e}")
            
            # Progress logging
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(articles) + batch_size - 1)//batch_size}")
        
        # Update final metrics
        self.metrics.processing_time = time.time() - start_time
        
        # Log comprehensive results
        logger.info(f"Batch processing complete:")
        logger.info(f"  Total processed: {self.metrics.total_processed}")
        logger.info(f"  Successful: {self.metrics.successful_processed}")
        logger.info(f"  Quality passed: {self.metrics.quality_passed}")
        logger.info(f"  Success rate: {self.metrics.success_rate():.2%}")
        logger.info(f"  Quality rate: {self.metrics.quality_rate():.2%}")
        logger.info(f"  Processing time: {self.metrics.processing_time:.2f}s")
        logger.info(f"  Articles/second: {self.metrics.articles_per_second():.2f}")
        
        return processed_articles
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get detailed processing metrics"""
        return {
            'total_processed': self.metrics.total_processed,
            'successful_processed': self.metrics.successful_processed,
            'failed_processed': self.metrics.failed_processed,
            'quality_passed': self.metrics.quality_passed,
            'quality_failed': self.metrics.quality_failed,
            'success_rate': self.metrics.success_rate(),
            'quality_rate': self.metrics.quality_rate(),
            'processing_time': self.metrics.processing_time,
            'articles_per_second': self.metrics.articles_per_second(),
            'sentiment_analysis_time': self.metrics.sentiment_analysis_time,
            'keyword_extraction_time': self.metrics.keyword_extraction_time,
            'avg_processing_time_per_article': (
                self.metrics.processing_time / self.metrics.total_processed
                if self.metrics.total_processed > 0 else 0
            )
        }
    
    def get_quality_report(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive quality report"""
        if not articles:
            return {'error': 'No articles provided'}
        
        try:
            quality_scores = [article.get('quality_score', 0) for article in articles]
            sentiment_scores = [article.get('sentiment_score', 0) for article in articles]
            
            # Quality distribution
            quality_distribution = {
                'excellent': sum(1 for score in quality_scores if score >= 0.9),
                'good': sum(1 for score in quality_scores if 0.7 <= score < 0.9),
                'fair': sum(1 for score in quality_scores if 0.5 <= score < 0.7),
                'poor': sum(1 for score in quality_scores if score < 0.5)
            }
            
            # Sentiment distribution
            sentiment_distribution = {}
            for article in articles:
                sentiment = article.get('sentiment_label', 'neutral')
                sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1
            
            # Category distribution
            category_distribution = {}
            for article in articles:
                category = article.get('category', 'general')
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            # Source analysis
            source_quality = defaultdict(list)
            for article in articles:
                source = article.get('source', 'Unknown')
                quality = article.get('quality_score', 0)
                source_quality[source].append(quality)
            
            source_stats = {}
            for source, qualities in source_quality.items():
                source_stats[source] = {
                    'article_count': len(qualities),
                    'avg_quality': sum(qualities) / len(qualities),
                    'min_quality': min(qualities),
                    'max_quality': max(qualities)
                }
            
            return {
                'total_articles': len(articles),
                'avg_quality_score': sum(quality_scores) / len(quality_scores),
                'avg_sentiment_score': sum(sentiment_scores) / len(sentiment_scores),
                'quality_distribution': quality_distribution,
                'sentiment_distribution': sentiment_distribution,
                'category_distribution': category_distribution,
                'source_statistics': dict(sorted(source_stats.items(), key=lambda x: x[1]['avg_quality'], reverse=True)[:10]),
                'processing_metrics': self.get_processing_metrics()
            }
            
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return {'error': str(e)}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get processor health status"""
        try:
            return {
                'status': 'healthy',
                'metrics': self.get_processing_metrics(),
                'stop_words_count': len(self.stop_words),
                'category_patterns_count': len(self.category_patterns),
                'last_processing_time': self.metrics.processing_time,
                'performance_score': min(1.0, self.metrics.articles_per_second() / 10.0)  # Normalized score
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

if __name__ == "__main__":
    print("Testing enhanced news processor...")
    processor = NewsProcessor()
    
    # Test article
    test_article = {
        'title': 'Revolutionary AI Technology Transforms Healthcare Industry with Machine Learning',
        'description': 'This groundbreaking artificial intelligence breakthrough promises to revolutionize medical diagnosis and treatment using advanced machine learning algorithms.',
        'url': 'https://example.com/ai-healthcare',
        'source': 'TechNews',
        'category': 'search',
        'published_at': config.get_timestamp()
    }
    
    print("\n🔍 Testing enhanced processing...")
    processed = processor.process_article(test_article)
    
    if processed:
        print(f"Title: {processed['title']}")
        print(f"Sentiment: {processed['sentiment_label']} ({processed['sentiment_score']}) - Confidence: {processed['sentiment_confidence']}")
        print(f"Keywords: {processed['keywords']}")
        print(f"Category: {processed['category']} - Confidence: {processed['category_confidence']}")
        print(f"Quality Score: {processed['quality_score']}")
        print(f"Readability: {processed['readability_score']}")
        print(f"Processing Time: {processed['processing_time']}s")
        
        # Test metrics
        metrics = processor.get_processing_metrics()
        print(f"\n📊 Processing Metrics:")
        print(f"  Success Rate: {metrics['success_rate']:.2%}")
        print(f"  Quality Rate: {metrics['quality_rate']:.2%}")
        print(f"  Articles/Second: {metrics['articles_per_second']:.2f}")
        
        # Test health status
        health = processor.get_health_status()
        print(f"\n🏥 Health Status: {health['status']}")
    
    logger.info("Enhanced news processor ready!")