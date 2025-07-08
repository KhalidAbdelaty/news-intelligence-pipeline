"""
Enhanced dashboard with real-time monitoring, advanced analytics, and health checks
Professional-grade interface with comprehensive metrics and alerting
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Import our enhanced modules
from storage import NewsDB
from ingest import NewsFetcher
from transform import NewsProcessor
import config

# Configure page
st.set_page_config(
    page_title=config.DASHBOARD_CONFIG['title'],
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging for dashboard
logger = logging.getLogger(__name__)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin-bottom: 1rem;
    }
    
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin-bottom: 1rem;
    }
    
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin-bottom: 1rem;
    }
    
    .performance-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-healthy { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-unhealthy { background-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Initialize components with caching
@st.cache_resource
def init_components():
    """Initialize all pipeline components"""
    try:
        db = NewsDB()
        fetcher = NewsFetcher()
        processor = NewsProcessor()
        logger.info("All components initialized successfully")
        return db, fetcher, processor
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        st.error(f"Failed to initialize components: {e}")
        return None, None, None

# Global components
db, fetcher, processor = init_components()

# Health check functions
def get_system_health():
    """Get comprehensive system health status"""
    try:
        health_status = {
            'overall': 'healthy',
            'components': {},
            'alerts': [],
            'metrics': {}
        }
        
        # Check database health
        if db:
            db_health = db.get_database_health()
            health_status['components']['database'] = db_health
            if db_health['status'] != 'healthy':
                health_status['overall'] = 'warning'
                health_status['alerts'].append(f"Database issue: {db_health.get('error', 'Unknown error')}")
        
        # Check ingestion health
        if fetcher:
            ingestion_health = fetcher.get_health_status()
            health_status['components']['ingestion'] = ingestion_health
            if ingestion_health['status'] != 'healthy':
                health_status['overall'] = 'unhealthy'
                health_status['alerts'].append(f"API issue: {ingestion_health.get('error', 'Unknown error')}")
        
        # Check processor health
        if processor:
            processor_health = processor.get_health_status()
            health_status['components']['processor'] = processor_health
            if processor_health['status'] != 'healthy':
                health_status['overall'] = 'warning'
                health_status['alerts'].append(f"Processor issue: {processor_health.get('error', 'Unknown error')}")
        
        # Check application health
        app_health = config.health_check()
        health_status['components']['application'] = app_health
        if app_health['status'] != 'healthy':
            health_status['overall'] = 'unhealthy'
            health_status['alerts'].append(f"Application issue: {app_health.get('error', 'Unknown error')}")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'overall': 'unhealthy',
            'components': {},
            'alerts': [f"Health check failed: {str(e)}"],
            'metrics': {}
        }

def display_health_indicator(status):
    """Display health status indicator"""
    status_class = {
        'healthy': 'status-healthy',
        'warning': 'status-warning',
        'unhealthy': 'status-unhealthy'
    }.get(status, 'status-unhealthy')
    
    return f'<span class="performance-indicator {status_class}"></span>{status.title()}'

def run_enhanced_pipeline():
    """Run the complete enhanced pipeline with monitoring"""
    run_id = f"enhanced_{int(time.time())}"
    
    # Create progress tracking
    progress_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        metrics_placeholder = st.empty()
    
    try:
        # Phase 1: Data Ingestion
        status_text.text("🔄 Phase 1/4: Enhanced data ingestion...")
        progress_bar.progress(10)
        
        start_time = time.time()
        articles = fetcher.run_full_fetch(run_id=run_id)
        ingestion_time = time.time() - start_time
        
        if not articles:
            st.error("No articles fetched. Check API connection and try again.")
            return False
        
        progress_bar.progress(35)
        
        # Phase 2: Data Processing
        status_text.text("🔄 Phase 2/4: Advanced processing and analysis...")
        
        processing_start = time.time()
        processed_articles = processor.process_articles_batch(articles)
        processing_time = time.time() - processing_start
        
        progress_bar.progress(65)
        
        # Phase 3: Data Storage
        status_text.text("🔄 Phase 3/4: Storing with quality checks...")
        
        storage_start = time.time()
        saved_count = db.save_articles_batch(processed_articles, run_id=run_id)
        storage_time = time.time() - storage_start
        
        progress_bar.progress(90)
        
        # Phase 4: Quality Report
        status_text.text("🔄 Phase 4/4: Generating quality report...")
        
        quality_report = processor.get_quality_report(processed_articles)
        ingestion_metrics = fetcher.get_ingestion_metrics()
        
        progress_bar.progress(100)
        
        # Display comprehensive results
        total_time = time.time() - start_time
        
        # Success summary
        success_col1, success_col2, success_col3, success_col4 = st.columns(4)
        
        with success_col1:
            st.metric("Articles Processed", len(processed_articles))
        
        with success_col2:
            st.metric("Articles Saved", saved_count)
        
        with success_col3:
            st.metric("Success Rate", f"{ingestion_metrics['success_rate']:.1%}")
        
        with success_col4:
            st.metric("Total Time", f"{total_time:.1f}s")
        
        # Detailed metrics
        with st.expander("📊 Detailed Pipeline Metrics"):
            metrics_col1, metrics_col2 = st.columns(2)
            
            with metrics_col1:
                st.write("**Ingestion Metrics:**")
                st.write(f"- API Requests: {ingestion_metrics['total_requests']}")
                st.write(f"- Success Rate: {ingestion_metrics['success_rate']:.2%}")
                st.write(f"- Articles/Second: {ingestion_metrics['articles_per_second']:.2f}")
                st.write(f"- Rate Limit Hits: {ingestion_metrics['rate_limit_hits']}")
                st.write(f"- Retries: {ingestion_metrics['retries_attempted']}")
            
            with metrics_col2:
                st.write("**Processing Metrics:**")
                processing_metrics = processor.get_processing_metrics()
                st.write(f"- Quality Rate: {processing_metrics['quality_rate']:.2%}")
                st.write(f"- Avg Quality Score: {quality_report['avg_quality_score']:.3f}")
                st.write(f"- Processing Time: {processing_time:.2f}s")
                st.write(f"- Sentiment Analysis: {processing_metrics['sentiment_analysis_time']:.2f}s")
                st.write(f"- Keyword Extraction: {processing_metrics['keyword_extraction_time']:.2f}s")
        
        status_text.text("✅ Pipeline completed successfully!")
        time.sleep(2)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        metrics_placeholder.empty()
        
        return True
        
    except Exception as e:
        logger.error(f"Enhanced pipeline failed: {e}")
        st.error(f"Pipeline failed: {str(e)}")
        return False

def display_advanced_analytics():
    """Display advanced analytics and insights"""
    st.header("🧠 Advanced Analytics")
    
    # Get articles with enhanced features
    articles_df = db.get_articles(limit=500, min_quality=0.6)
    
    if articles_df.empty:
        st.warning("No high-quality articles found. Run the pipeline to generate data.")
        return
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Quality Analysis", "🔥 Trending Topics", "📈 Performance", "🎯 Insights"])
    
    with tab1:
        display_quality_analysis(articles_df)
    
    with tab2:
        display_trending_analysis(articles_df)
    
    with tab3:
        display_performance_metrics()
    
    with tab4:
        display_insights_dashboard(articles_df)

def display_quality_analysis(articles_df):
    """Display comprehensive quality analysis"""
    st.subheader("Data Quality Dashboard")
    
    # Quality metrics
    quality_col1, quality_col2, quality_col3, quality_col4 = st.columns(4)
    
    with quality_col1:
        avg_quality = articles_df['quality_score'].mean()
        st.metric("Avg Quality Score", f"{avg_quality:.3f}")
    
    with quality_col2:
        high_quality_count = len(articles_df[articles_df['quality_score'] >= 0.8])
        st.metric("High Quality Articles", high_quality_count)
    
    with quality_col3:
        unique_sources = articles_df['source'].nunique()
        st.metric("Unique Sources", unique_sources)
    
    with quality_col4:
        avg_readability = articles_df.get('readability_score', pd.Series([0.5])).mean()
        st.metric("Avg Readability", f"{avg_readability:.3f}")
    
    # Quality distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality score distribution
        quality_bins = pd.cut(articles_df['quality_score'], 
                             bins=[0, 0.5, 0.7, 0.9, 1.0], 
                             labels=['Poor', 'Fair', 'Good', 'Excellent'])
        quality_counts = quality_bins.value_counts()
        
        fig_quality = px.pie(
            values=quality_counts.values,
            names=quality_counts.index,
            title="Quality Distribution",
            color_discrete_map={
                'Excellent': '#28a745',
                'Good': '#17a2b8',
                'Fair': '#ffc107',
                'Poor': '#dc3545'
            }
        )
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Source quality comparison
        source_quality = articles_df.groupby('source').agg({
            'quality_score': 'mean',
            'title': 'count'
        }).round(3)
        source_quality.columns = ['Avg Quality', 'Article Count']
        source_quality = source_quality.sort_values('Avg Quality', ascending=False).head(10)
        
        fig_source = px.bar(
            x=source_quality['Avg Quality'],
            y=source_quality.index,
            orientation='h',
            title="Source Quality Ranking",
            labels={'x': 'Average Quality Score', 'y': 'Source'}
        )
        fig_source.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_source, use_container_width=True)
    
    # Quality over time
    if 'created_at' in articles_df.columns:
        st.subheader("Quality Trends Over Time")
        
        articles_df['created_at'] = pd.to_datetime(articles_df['created_at'])
        daily_quality = articles_df.groupby(articles_df['created_at'].dt.date).agg({
            'quality_score': 'mean',
            'title': 'count'
        }).reset_index()
        
        fig_timeline = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Average Quality Score', 'Articles Per Day'),
            vertical_spacing=0.1
        )
        
        fig_timeline.add_trace(
            go.Scatter(x=daily_quality['created_at'], y=daily_quality['quality_score'],
                      mode='lines+markers', name='Quality Score'),
            row=1, col=1
        )
        
        fig_timeline.add_trace(
            go.Bar(x=daily_quality['created_at'], y=daily_quality['title'],
                   name='Article Count'),
            row=2, col=1
        )
        
        fig_timeline.update_layout(height=500, title_text="Quality and Volume Trends")
        st.plotly_chart(fig_timeline, use_container_width=True)

def display_trending_analysis(articles_df):
    """Display trending topics analysis"""
    st.subheader("Trending Topics Analysis")
    
    # Get trending topics from processor
    articles_list = articles_df.to_dict('records')
    trending_topics = processor.detect_trending_topics(articles_list)
    
    if trending_topics:
        # Display top trending topics
        trending_col1, trending_col2 = st.columns(2)
        
        with trending_col1:
            st.write("**🔥 Top Trending Topics**")
            
            trending_df = pd.DataFrame(trending_topics[:10])
            
            fig_trending = px.bar(
                trending_df,
                x='trending_score',
                y='keyword',
                orientation='h',
                title="Trending Score by Keyword",
                labels={'trending_score': 'Trending Score', 'keyword': 'Keyword'}
            )
            fig_trending.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_trending, use_container_width=True)
        
        with trending_col2:
            st.write("**📊 Trending Details**")
            
            for topic in trending_topics[:5]:
                with st.expander(f"📈 {topic['keyword']} (Score: {topic['trending_score']})"):
                    st.write(f"**Total Mentions:** {topic['total_mentions']}")
                    st.write(f"**Trend Velocity:** {topic['trend_velocity']}")
                    st.write(f"**Source Diversity:** {topic['source_diversity']}")
                    st.write(f"**Avg Sentiment:** {topic['avg_sentiment']:.3f}")
                    st.write(f"**Sentiment Consistency:** {topic['sentiment_consistency']:.3f}")
        
        # Trending topics table
        st.subheader("Complete Trending Topics Table")
        
        trending_display = pd.DataFrame(trending_topics)
        st.dataframe(
            trending_display[['keyword', 'trending_score', 'total_mentions', 
                            'trend_velocity', 'source_diversity', 'avg_sentiment']],
            use_container_width=True
        )
    
    else:
        st.info("Not enough data to detect trending topics. Run the pipeline multiple times to build trend data.")

def display_performance_metrics():
    """Display system performance metrics"""
    st.subheader("System Performance Monitoring")
    
    # Get performance data
    if db:
        performance_df = db.get_performance_metrics()
        
        if not performance_df.empty:
            perf_col1, perf_col2 = st.columns(2)
            
            with perf_col1:
                # Processing time metrics
                processing_metrics = performance_df[performance_df['metric_name'] == 'article_processing_time']
                
                if not processing_metrics.empty:
                    st.metric("Avg Processing Time", f"{processing_metrics['avg_value'].iloc[0]:.4f}s")
                    st.metric("Max Processing Time", f"{processing_metrics['max_value'].iloc[0]:.4f}s")
                    st.metric("Min Processing Time", f"{processing_metrics['min_value'].iloc[0]:.4f}s")
            
            with perf_col2:
                # Quality score metrics
                quality_metrics = performance_df[performance_df['metric_name'] == 'article_quality_score']
                
                if not quality_metrics.empty:
                    st.metric("Avg Quality Score", f"{quality_metrics['avg_value'].iloc[0]:.3f}")
                    st.metric("Max Quality Score", f"{quality_metrics['max_value'].iloc[0]:.3f}")
                    st.metric("Min Quality Score", f"{quality_metrics['min_value'].iloc[0]:.3f}")
            
            # Performance trends
            st.subheader("Performance Trends")
            
            if len(performance_df) > 1:
                fig_perf = px.bar(
                    performance_df,
                    x='metric_name',
                    y='avg_value',
                    title="Average Performance Metrics",
                    labels={'avg_value': 'Average Value', 'metric_name': 'Metric'}
                )
                st.plotly_chart(fig_perf, use_container_width=True)
            else:
                st.info("Run the pipeline multiple times to see performance trends.")
        else:
            st.info("No performance metrics available. Run the pipeline to generate data.")

def display_insights_dashboard(articles_df):
    """Display actionable insights"""
    st.subheader("Actionable Insights")
    
    # Generate insights
    insights = []
    
    # Quality insights
    low_quality_sources = articles_df[articles_df['quality_score'] < 0.6]['source'].value_counts()
    if not low_quality_sources.empty:
        insights.append({
            'type': 'warning',
            'title': 'Low Quality Sources Detected',
            'message': f"Sources with quality issues: {', '.join(low_quality_sources.head(3).index)}",
            'action': 'Consider filtering or improving data from these sources'
        })
    
    # Sentiment insights
    negative_sentiment = articles_df[articles_df['sentiment_label'] == 'negative']
    if len(negative_sentiment) > len(articles_df) * 0.4:
        insights.append({
            'type': 'warning',
            'title': 'High Negative Sentiment',
            'message': f"{len(negative_sentiment)} articles ({len(negative_sentiment)/len(articles_df)*100:.1f}%) have negative sentiment",
            'action': 'Monitor for potential crisis or negative trend'
        })
    
    # Source diversity insights
    source_counts = articles_df['source'].value_counts()
    if source_counts.iloc[0] > len(articles_df) * 0.5:
        insights.append({
            'type': 'info',
            'title': 'Source Concentration',
            'message': f"Over 50% of articles come from {source_counts.index[0]}",
            'action': 'Consider diversifying news sources for better coverage'
        })
    
    # Category insights
    category_counts = articles_df['category'].value_counts()
    dominant_category = category_counts.index[0]
    if category_counts.iloc[0] > len(articles_df) * 0.4:
        insights.append({
            'type': 'info',
            'title': 'Category Dominance',
            'message': f"40%+ of articles are about {dominant_category}",
            'action': 'Current trend focus detected in this category'
        })
    
    # Display insights
    if insights:
        for insight in insights:
            alert_class = {
                'warning': 'alert-warning',
                'info': 'alert-success',
                'error': 'alert-danger'
            }.get(insight['type'], 'alert-success')
            
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{insight['title']}</strong><br>
                {insight['message']}<br>
                <em>Action: {insight['action']}</em>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No significant issues detected. System is performing well!")

def main():
    """Enhanced main dashboard function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📰 News Intelligence Pipeline</h1>
        <p>Professional-grade news analytics with real-time monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System Health Dashboard
    st.header("🏥 System Health")
    
    health_status = get_system_health()
    
    # Health overview
    health_col1, health_col2, health_col3, health_col4 = st.columns(4)
    
    with health_col1:
        overall_status = health_status['overall']
        st.markdown(f"**Overall Status:** {display_health_indicator(overall_status)}", unsafe_allow_html=True)
    
    with health_col2:
        db_status = health_status['components'].get('database', {}).get('status', 'unknown')
        st.markdown(f"**Database:** {display_health_indicator(db_status)}", unsafe_allow_html=True)
    
    with health_col3:
        api_status = health_status['components'].get('ingestion', {}).get('status', 'unknown')
        st.markdown(f"**API:** {display_health_indicator(api_status)}", unsafe_allow_html=True)
    
    with health_col4:
        proc_status = health_status['components'].get('processor', {}).get('status', 'unknown')
        st.markdown(f"**Processor:** {display_health_indicator(proc_status)}", unsafe_allow_html=True)
    
    # Alerts
    if health_status['alerts']:
        st.error("⚠️ System Alerts:")
        for alert in health_status['alerts']:
            st.error(f"• {alert}")
    
    # Sidebar Controls
    st.sidebar.header("🔧 Pipeline Controls")
    
    # Enhanced pipeline button
    if st.sidebar.button("🚀 Run Enhanced Pipeline", type="primary"):
        with st.spinner("Running enhanced pipeline..."):
            if run_enhanced_pipeline():
                st.rerun()
    
    # Quick actions
    st.sidebar.subheader("Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    if st.sidebar.button("🧹 Clear Cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache cleared!")
    
    # Real-time processing toggle
    st.sidebar.subheader("Real-time Processing")
    
    if config.REALTIME_CONFIG['enabled']:
        realtime_status = "🟢 Available"
        if st.sidebar.button("▶️ Start Real-time"):
            if fetcher:
                def realtime_callback(articles):
                    logger.info(f"Real-time processing: {len(articles)} articles")
                
                fetcher.start_realtime_processing(callback=realtime_callback)
                st.sidebar.success("Real-time processing started!")
        
        if st.sidebar.button("⏹️ Stop Real-time"):
            if fetcher:
                fetcher.stop_realtime_processing()
                st.sidebar.success("Real-time processing stopped!")
    else:
        realtime_status = "🔴 Disabled"
    
    st.sidebar.write(f"Status: {realtime_status}")
    
    # Settings
    st.sidebar.subheader("📊 Display Settings")
    
    max_articles = st.sidebar.slider("Max Articles", 10, 1000, 200)
    min_quality = st.sidebar.slider("Min Quality Score", 0.0, 1.0, 0.5, 0.1)
    
    # Time range filter
    time_range = st.sidebar.selectbox(
        "Time Range",
        ["Last 24 hours", "Last 3 days", "Last 7 days", "Last 30 days", "All time"]
    )
    
    # Main Content
    if not db or not fetcher or not processor:
        st.error("System components not properly initialized. Please check logs.")
        return
    
    # Get articles
    articles_df = db.get_articles(limit=max_articles, min_quality=min_quality)
    
    if articles_df.empty:
        st.warning("📭 No articles found. Run the enhanced pipeline to fetch and process news data!")
        st.info("👆 Click 'Run Enhanced Pipeline' in the sidebar to get started")
        return
    
    # Enhanced Analytics
    display_advanced_analytics()
    
    # Traditional Dashboard Components
    st.header("📊 Overview Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Articles", len(articles_df))
    
    with col2:
        avg_sentiment = articles_df['sentiment_score'].mean()
        st.metric("Avg Sentiment", f"{avg_sentiment:.3f}")
    
    with col3:
        unique_sources = articles_df['source'].nunique()
        st.metric("News Sources", unique_sources)
    
    with col4:
        avg_quality = articles_df.get('quality_score', pd.Series([0.5])).mean()
        st.metric("Avg Quality", f"{avg_quality:.3f}")
    
    # Sentiment Analysis
    st.header("💭 Sentiment Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sentiment_counts = articles_df['sentiment_label'].value_counts()
        
        fig_pie = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Sentiment Distribution",
            color_discrete_map={
                'positive': '#28a745',
                'negative': '#dc3545',
                'neutral': '#6c757d'
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Enhanced sentiment over time
        if 'created_at' in articles_df.columns:
            articles_df['created_at'] = pd.to_datetime(articles_df['created_at'])
            sentiment_time = articles_df.groupby([
                articles_df['created_at'].dt.date,
                'sentiment_label'
            ]).size().reset_index(name='count')
            
            fig_line = px.line(
                sentiment_time,
                x='created_at',
                y='count',
                color='sentiment_label',
                title="Sentiment Trends Over Time",
                color_discrete_map={
                    'positive': '#28a745',
                    'negative': '#dc3545',
                    'neutral': '#6c757d'
                }
            )
            st.plotly_chart(fig_line, use_container_width=True)
    
    # Article Search and Display
    st.header("📰 Article Explorer")
    
    # Enhanced search
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        search_term = st.text_input("🔍 Search articles", placeholder="Enter keywords...")
    
    with search_col2:
        category_filter = st.selectbox("Category", ["All"] + list(articles_df['category'].unique()))
    
    # Apply filters
    display_articles = articles_df.copy()
    
    if search_term:
        search_results = db.search_articles(search_term, limit=max_articles)
        if not search_results.empty:
            display_articles = search_results
        else:
            st.info(f"No articles found for '{search_term}'")
    
    if category_filter != "All":
        display_articles = display_articles[display_articles['category'] == category_filter]
    
    # Display articles with enhanced information
    for idx, article in display_articles.head(50).iterrows():
        with st.expander(f"📄 {article['title'][:100]}... | {article['source']}"):
            
            article_col1, article_col2 = st.columns([3, 1])
            
            with article_col1:
                st.write(f"**Description:** {article['description']}")
                st.write(f"**URL:** {article['url']}")
                if article.get('keywords'):
                    st.write(f"**Keywords:** {article['keywords']}")
                
                # Enhanced metadata
                if article.get('quality_score'):
                    st.write(f"**Quality Score:** {article['quality_score']:.3f}")
                
                if article.get('category_confidence'):
                    st.write(f"**Category Confidence:** {article['category_confidence']:.3f}")
            
            with article_col2:
                # Sentiment with enhanced display
                sentiment = article['sentiment_label']
                score = article['sentiment_score']
                confidence = article.get('sentiment_confidence', 0)
                
                if sentiment == 'positive':
                    st.success(f"😊 {sentiment.title()}")
                elif sentiment == 'negative':
                    st.error(f"😞 {sentiment.title()}")
                else:
                    st.info(f"😐 {sentiment.title()}")
                
                st.write(f"**Score:** {score:.3f}")
                if confidence:
                    st.write(f"**Confidence:** {confidence:.3f}")
                
                st.write(f"**Category:** {article['category']}")
                
                # Processing info
                if article.get('processing_time'):
                    st.write(f"**Processing:** {article['processing_time']:.4f}s")
    
    # Footer with system info
    st.markdown("---")
    
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("*Built with Python 3.11.9*")
    
    with footer_col2:
        st.markdown("*Streamlit + GNews API*")
    
    with footer_col3:
        st.markdown(f"*Environment: {config.ENVIRONMENT}*")
    
    # Auto-refresh
    if st.sidebar.checkbox("🔄 Auto-refresh") and config.DASHBOARD_CONFIG['auto_refresh']:
        time.sleep(config.DASHBOARD_CONFIG['refresh_interval'])
        st.rerun()

if __name__ == "__main__":
    main()