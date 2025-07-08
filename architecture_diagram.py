from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECS, Lambda
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, CloudFront
from diagrams.aws.storage import S3
from diagrams.aws.analytics import Athena
from diagrams.onprem.client import Users
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.monitoring import Prometheus
from diagrams.programming.language import Python
from diagrams.generic.network import Firewall
from diagrams.generic.database import SQL
from diagrams.generic.compute import Rack

# High-quality diagram settings
DIAGRAM_SETTINGS = {
    "graph_attr": {
        "fontsize": "28",
        "bgcolor": "white",
        "dpi": "300",
        "fontname": "Arial",
        "splines": "ortho",
        "nodesep": "1",
        "ranksep": "2"
    },
    "node_attr": {
        "fontsize": "14",
        "fontname": "Arial Bold"
    },
    "edge_attr": {
        "fontsize": "12",
        "fontname": "Arial"
    }
}

def create_local_architecture():
    """Create local development architecture diagram - FIXED"""
    
    with Diagram("News Intelligence Pipeline - Local Development", 
                 show=False, 
                 direction="TB",
                 filename="architecture_local",
                 outformat=["png", "svg"],
                 **DIAGRAM_SETTINGS):
        
        # External APIs
        with Cluster("External Data Sources", graph_attr={"bgcolor": "#e8f4fd", "style": "rounded"}):
            gnews_api = Firewall("GNews API\n• 60,000+ Sources\n• Rate Limited\n• Real-time")
        
        # Core Pipeline Components
        with Cluster("News Intelligence Pipeline", graph_attr={"bgcolor": "#f0f8f0", "style": "rounded"}):
            
            with Cluster("01. Data Ingestion Layer"):
                ingest_module = Python("ingest.py\n• Concurrent Processing\n• Error Handling\n• Rate Limiting")
            
            with Cluster("02. Data Processing Layer"):
                transform_module = Python("transform.py\n• NLP & Sentiment Analysis\n• Quality Validation\n• Keyword Extraction")
            
            with Cluster("03. Data Storage Layer"):
                storage_module = SQL("storage.py\n• SQLite Database\n• Optimized Queries\n• Quality Tracking")
            
            with Cluster("04. Configuration Layer"):
                config_module = Python("config.py\n• Environment Settings\n• Health Monitoring\n• Performance Metrics")
            
            with Cluster("05. Presentation Layer"):
                dashboard_module = Python("dashboard.py\n• Streamlit Dashboard\n• Interactive Analytics\n• Real-time Updates")
        
        # End Users
        users = Users("End Users\n• Data Engineers\n• Business Analysts\n• Decision Makers")
        
        # Data Flow - Fixed connections (no list-to-list operations)
        gnews_api >> Edge(label="HTTP Requests\n1 req/sec", color="#2E86AB", style="bold") >> ingest_module
        ingest_module >> Edge(label="Raw JSON Data\n500+ articles/run", color="#A23B72", style="bold") >> transform_module
        transform_module >> Edge(label="Processed Data\nSentiment + Keywords", color="#F18F01", style="bold") >> storage_module
        storage_module >> Edge(label="Structured Data\nSQL Queries", color="#C73E1D", style="bold") >> dashboard_module
        
        # Configuration connections (dashed)
        config_module >> Edge(label="Config", style="dashed", color="#6C757D") >> ingest_module
        config_module >> Edge(label="Settings", style="dashed", color="#6C757D") >> transform_module
        config_module >> Edge(label="Monitoring", style="dashed", color="#6C757D") >> storage_module
        
        # User interaction
        dashboard_module >> Edge(label="Web Interface\nPort 8501", color="#28A745", style="bold") >> users

def create_production_architecture():
    """Create production/cloud architecture diagram - FIXED"""
    
    with Diagram("News Intelligence Pipeline - Production Architecture", 
                 show=False, 
                 direction="TB",
                 filename="architecture_production",
                 outformat=["png", "svg"],
                 **DIAGRAM_SETTINGS):
        
        # User Layer
        users = Users("Global Users\n• 1000+ Concurrent\n• Multi-region")
        cdn = CloudFront("CloudFront CDN\n• Global Distribution\n• Edge Caching")
        lb = ELB("Application LB\n• Auto Scaling\n• Health Checks")
        
        # External APIs
        with Cluster("External APIs", graph_attr={"bgcolor": "#fff2e6", "style": "rounded"}):
            gnews_api = Firewall("GNews API\n• Enterprise Tier\n• SLA Guaranteed")
        
        # Application Layer
        with Cluster("Containerized Services", graph_attr={"bgcolor": "#e6f3ff", "style": "rounded"}):
            # Individual containers (not list)
            container1 = ECS("Pipeline Service 1\n• Auto Scaling\n• Health Monitoring")
            container2 = ECS("Pipeline Service 2\n• Load Balanced\n• Fault Tolerant")
            container3 = ECS("Pipeline Service 3\n• High Availability\n• Performance Optimized")
        
        # Serverless Layer
        with Cluster("Serverless Functions", graph_attr={"bgcolor": "#f0f8e6", "style": "rounded"}):
            lambda_ingest = Lambda("Ingestion Lambda\n• Event Triggered\n• Auto Scaling")
            lambda_process = Lambda("Processing Lambda\n• Batch Jobs\n• Scheduled Runs")
        
        # Data Layer
        with Cluster("Data Infrastructure", graph_attr={"bgcolor": "#f5f0ff", "style": "rounded"}):
            rds_primary = RDS("PostgreSQL Primary\n• Multi-AZ\n• Automated Backups")
            rds_replica = RDS("Read Replica\n• Cross-Region\n• Read Scaling")
            
            s3_raw = S3("Raw Data Lake\n• JSON Files\n• Versioned Storage")
            s3_processed = S3("Processed Data\n• Parquet Format\n• Partitioned")
        
        # Analytics & Monitoring
        with Cluster("Analytics Platform", graph_attr={"bgcolor": "#fff0f5", "style": "rounded"}):
            athena = Athena("Query Engine\n• Serverless SQL\n• Cost Optimized")
            monitoring = Prometheus("Monitoring\n• Real-time Metrics\n• Alerting")
        
        # User Flow - Fixed connections
        users >> Edge(label="HTTPS", color="#28A745") >> cdn
        cdn >> Edge(label="Cached Content", color="#007BFF") >> lb
        
        # Load balancer to containers (individual connections)
        lb >> Edge(label="Traffic Distribution", color="#6F42C1") >> container1
        lb >> Edge(label="Load Balanced", color="#6F42C1") >> container2
        lb >> Edge(label="High Availability", color="#6F42C1") >> container3
        
        # API to serverless
        gnews_api >> Edge(label="Real-time Data\n100 req/min", color="#FD7E14") >> lambda_ingest
        
        # Data pipeline flow
        lambda_ingest >> Edge(label="Raw JSON", color="#20C997") >> s3_raw
        s3_raw >> Edge(label="S3 Event Trigger", color="#E83E8C") >> lambda_process
        lambda_process >> Edge(label="Processed Data", color="#6610F2") >> s3_processed
        lambda_process >> Edge(label="Structured Data", color="#DC3545") >> rds_primary
        
        # Database replication
        rds_primary >> Edge(label="Async Replication", style="dashed", color="#6C757D") >> rds_replica
        
        # Container connections to data
        container1 >> Edge(label="Read Queries", color="#17A2B8") >> rds_replica
        container2 >> Edge(label="Read Operations", color="#17A2B8") >> rds_replica
        container3 >> Edge(label="Read Access", color="#17A2B8") >> rds_replica
        
        container1 >> Edge(label="Write Ops", color="#DC3545") >> rds_primary
        
        # Analytics connections
        s3_processed >> Edge(label="SQL Queries", color="#FFC107") >> athena
        
        # Monitoring connections (dashed)
        container1 >> Edge(label="Metrics", style="dashed", color="#6C757D") >> monitoring
        lambda_ingest >> Edge(label="Logs", style="dashed", color="#6C757D") >> monitoring
        lambda_process >> Edge(label="Performance", style="dashed", color="#6C757D") >> monitoring

def create_data_flow_diagram():
    """Create detailed data flow diagram - FIXED"""
    
    with Diagram("News Intelligence Pipeline - Data Flow Architecture", 
                 show=False, 
                 direction="LR",
                 filename="data_flow",
                 outformat=["png", "svg"],
                 **DIAGRAM_SETTINGS):
        
        # Data Sources
        with Cluster("Data Sources", graph_attr={"bgcolor": "#ffe6e6", "style": "rounded"}):
            source1 = Firewall("Global News\n• 60,000+ Sources")
            source2 = Firewall("Real-time API\n• Live Updates")
            source3 = Firewall("Historical Data\n• Archive Access")
        
        # Ingestion Layer
        with Cluster("Ingestion Layer", graph_attr={"bgcolor": "#e6f2ff", "style": "rounded"}):
            api_client = Python("API Client\n• Authentication\n• Rate Limiting")
            validator = Rack("Data Validator\n• Schema Check\n• Quality Gate")
        
        # Processing Layer
        with Cluster("Processing Engine", graph_attr={"bgcolor": "#f0f8e6", "style": "rounded"}):
            nlp_engine = Python("NLP Processor\n• Text Cleaning\n• Language Detection")
            sentiment_engine = Python("Sentiment Analyzer\n• Polarity Scoring\n• Confidence Rating")
            keyword_engine = Python("Keyword Extractor\n• TF-IDF Algorithm\n• N-gram Analysis")
            category_engine = Python("Auto Categorizer\n• ML Classification\n• 9 Categories")
        
        # Storage Layer
        with Cluster("Data Storage", graph_attr={"bgcolor": "#f5f0ff", "style": "rounded"}):
            raw_db = SQL("Raw Articles\n• JSON Format\n• Full Text Index")
            processed_db = SQL("Processed Data\n• Normalized Schema\n• Optimized Queries")
            metrics_db = SQL("Quality Metrics\n• Performance Data\n• Audit Trail")
        
        # Analytics Layer
        with Cluster("Analytics Engine", graph_attr={"bgcolor": "#fff5e6", "style": "rounded"}):
            trend_analyzer = Python("Trend Analyzer\n• Temporal Patterns\n• Velocity Tracking")
            quality_monitor = Prometheus("Quality Monitor\n• Data Validation\n• SLA Tracking")
        
        # Presentation Layer
        with Cluster("User Interface", graph_attr={"bgcolor": "#e6ffe6", "style": "rounded"}):
            dashboard = Python("Interactive Dashboard\n• Real-time Updates\n• Export Features")
            api_server = Python("REST API\n• Health Endpoints\n• Metrics API")
        
        # Data Flow - Individual connections (no list operations)
        source1 >> Edge(label="HTTP/JSON", color="#007BFF") >> api_client
        source2 >> Edge(label="Real-time", color="#28A745") >> api_client  
        source3 >> Edge(label="Batch", color="#FFC107") >> api_client
        
        api_client >> Edge(label="Validated Data", color="#17A2B8") >> validator
        validator >> Edge(label="Clean Data", color="#20C997") >> nlp_engine
        
        nlp_engine >> Edge(label="Processed Text", color="#6F42C1") >> sentiment_engine
        sentiment_engine >> Edge(label="Sentiment Scores", color="#E83E8C") >> keyword_engine
        keyword_engine >> Edge(label="Keywords", color="#FD7E14") >> category_engine
        
        category_engine >> Edge(label="Enriched Data", color="#DC3545") >> raw_db
        category_engine >> Edge(label="Structured Data", color="#198754") >> processed_db
        validator >> Edge(label="Quality Data", color="#6C757D") >> metrics_db
        
        processed_db >> Edge(label="Time Series", color="#0D6EFD") >> trend_analyzer
        metrics_db >> Edge(label="Quality Stats", color="#B02A37") >> quality_monitor
        
        trend_analyzer >> Edge(label="Insights", color="#6610F2") >> dashboard
        quality_monitor >> Edge(label="Reports", color="#D63384") >> dashboard
        processed_db >> Edge(label="API Data", color="#0DCAF0") >> api_server

def create_technology_stack_diagram():
    """Create technology stack diagram - FIXED"""
    
    with Diagram("News Intelligence Pipeline - Technology Stack", 
                 show=False, 
                 direction="TB",
                 filename="technology_stack",
                 outformat=["png", "svg"],
                 **DIAGRAM_SETTINGS):
        
        # Presentation Layer
        with Cluster("Presentation Layer", graph_attr={"bgcolor": "#e6f3ff", "style": "rounded"}):
            ui_streamlit = Python("Streamlit 1.31\n• Interactive UI\n• Real-time Updates")
            ui_plotly = Python("Plotly 5.18\n• Data Visualization\n• Interactive Charts")
            ui_css = Python("Custom Styling\n• Professional Theme\n• Responsive Design")
        
        # Application Layer
        with Cluster("Application Layer", graph_attr={"bgcolor": "#f0f8e6", "style": "rounded"}):
            app_python = Python("Python 3.11.9\n• Core Language\n• Async Support")
            app_pandas = Python("Pandas 2.2\n• Data Manipulation\n• High Performance")
            app_textblob = Python("TextBlob 0.17\n• NLP Processing\n• Sentiment Analysis")
            app_requests = Python("Requests 2.31\n• HTTP Client\n• API Integration")
        
        # Data Layer
        with Cluster("Data Layer", graph_attr={"bgcolor": "#fff0f5", "style": "rounded"}):
            data_sqlite = SQL("SQLite\n• Local Development\n• File-based Storage")
            data_postgres = PostgreSQL("PostgreSQL 15\n• Production Database\n• ACID Compliance")
            data_optimization = SQL("Query Optimization\n• Indexing Strategy\n• Performance Tuning")
        
        # Infrastructure Layer
        with Cluster("Infrastructure Layer", graph_attr={"bgcolor": "#f5f0ff", "style": "rounded"}):
            infra_docker = ECS("Docker\n• Containerization\n• Multi-stage Builds")
            infra_actions = Lambda("GitHub Actions\n• CI/CD Pipeline\n• Automated Testing")
            infra_cloud = ECS("Cloud Services\n• AWS/Azure/GCP\n• Auto Scaling")
        
        # Monitoring Layer
        with Cluster("Monitoring & Quality", graph_attr={"bgcolor": "#ffe6e6", "style": "rounded"}):
            monitor_logging = Prometheus("Structured Logging\n• Performance Metrics\n• Error Tracking")
            monitor_security = Firewall("Security Layer\n• Input Validation\n• API Authentication")
            monitor_quality = Rack("Quality Assurance\n• Data Validation\n• Automated Testing")
        
        # Technology Stack Relationships - Individual connections
        ui_streamlit >> Edge(label="Renders UI", color="#E74C3C") >> app_python
        ui_plotly >> Edge(label="Visualizations", color="#3498DB") >> app_python
        ui_css >> Edge(label="Styling", color="#9B59B6") >> app_python
        
        app_python >> Edge(label="Data Ops", color="#2ECC71") >> app_pandas
        app_python >> Edge(label="NLP Tasks", color="#F39C12") >> app_textblob
        app_python >> Edge(label="API Calls", color="#1ABC9C") >> app_requests
        
        app_pandas >> Edge(label="Dev Storage", color="#34495E") >> data_sqlite
        app_pandas >> Edge(label="Prod Storage", color="#2C3E50") >> data_postgres
        app_pandas >> Edge(label="Optimization", color="#7F8C8D") >> data_optimization
        
        app_python >> Edge(label="Containerized", color="#E67E22") >> infra_docker
        app_python >> Edge(label="CI/CD", color="#8E44AD") >> infra_actions
        infra_docker >> Edge(label="Deployed", color="#16A085") >> infra_cloud
        
        app_python >> Edge(label="Logs", style="dashed", color="#95A5A6") >> monitor_logging
        app_requests >> Edge(label="Security", style="dashed", color="#C0392B") >> monitor_security
        app_pandas >> Edge(label="Quality", style="dashed", color="#D35400") >> monitor_quality

def create_deployment_diagram():
    """Create deployment options diagram - FIXED"""
    
    with Diagram("News Intelligence Pipeline - Deployment Options", 
                 show=False, 
                 direction="TB",
                 filename="deployment_options",
                 outformat=["png", "svg"],
                 **DIAGRAM_SETTINGS):
        
        # Source Code
        source_code = Python("Source Code\n• 5 Python Files\n• Clean Architecture\n• Production Ready")
        
        # Development Environment
        with Cluster("Local Development", graph_attr={"bgcolor": "#f0f8ff", "style": "rounded"}):
            local_sqlite = SQL("SQLite Database\n• File-based\n• Zero Configuration")
            local_streamlit = Python("Streamlit Server\n• Development Mode\n• Hot Reload")
            local_processing = Rack("Local Processing\n• Debug Mode\n• Full Logging")
        
        # Containerization
        with Cluster("Containerization", graph_attr={"bgcolor": "#f5f5f0", "style": "rounded"}):
            docker_container = ECS("Docker Container\n• Multi-stage Build\n• Optimized Layers")
            docker_compose = ECS("Docker Compose\n• Local Orchestration\n• Service Dependencies")
        
        # Cloud Deployment - AWS
        with Cluster("AWS Cloud Platform", graph_attr={"bgcolor": "#fff2e6", "style": "rounded"}):
            aws_fargate = ECS("ECS Fargate\n• Serverless Containers\n• Auto Scaling")
            aws_lambda = Lambda("Lambda Functions\n• Event-driven\n• Pay-per-execution")
            aws_apprunner = ELB("App Runner\n• Fully Managed\n• Git Integration")
        
        # Alternative Cloud Platforms
        with Cluster("Multi-Cloud Options", graph_attr={"bgcolor": "#e6f3ff", "style": "rounded"}):
            azure_containers = ECS("Azure Container\nInstances\n• Managed Service")
            gcp_cloudrun = ECS("Google Cloud Run\n• Serverless Platform\n• Knative Based")
            railway_deploy = ECS("Railway Platform\n• One-click Deploy\n• Git Integration")
        
        # CI/CD Pipeline
        with Cluster("DevOps Pipeline", graph_attr={"bgcolor": "#f0fff0", "style": "rounded"}):
            github_actions = Python("GitHub Actions\n• Automated Testing\n• Multi-environment")
            security_scan = Firewall("Security Scanning\n• Vulnerability Detection\n• Compliance Checks")
            auto_deploy = ECS("Automated Deployment\n• Blue/Green Strategy\n• Rollback Support")
        
        # Deployment Flow - Individual connections
        source_code >> Edge(label="Local Development", color="#28A745") >> local_sqlite
        source_code >> Edge(label="Local Testing", color="#17A2B8") >> local_streamlit
        source_code >> Edge(label="Debug Mode", color="#FFC107") >> local_processing
        
        source_code >> Edge(label="Containerize", color="#6F42C1") >> docker_container
        docker_container >> Edge(label="Local Orchestration", color="#E83E8C") >> docker_compose
        
        docker_container >> Edge(label="AWS Deploy", color="#FD7E14") >> aws_fargate
        docker_container >> Edge(label="Serverless", color="#20C997") >> aws_lambda
        docker_container >> Edge(label="Managed Service", color="#0D6EFD") >> aws_apprunner
        
        docker_container >> Edge(label="Azure Deploy", color="#6610F2") >> azure_containers
        docker_container >> Edge(label="GCP Deploy", color="#D63384") >> gcp_cloudrun
        docker_container >> Edge(label="Railway Deploy", color="#FD7E14") >> railway_deploy
        
        source_code >> Edge(label="Git Push", color="#6C757D") >> github_actions
        github_actions >> Edge(label="Security Check", color="#DC3545") >> security_scan
        security_scan >> Edge(label="Deploy", color="#198754") >> auto_deploy
        auto_deploy >> Edge(label="Production", color="#0DCAF0") >> aws_fargate

if __name__ == "__main__":
    print("🎨 Generating FIXED High-Quality Architecture Diagrams...")
    print("📐 Creating PNG and SVG versions with 300 DPI quality...")
    
    try:
        print("\n🔨 Creating Local Architecture...")
        create_local_architecture()
        print("✅ Local architecture: architecture_local.png + .svg")
        
        print("\n☁️ Creating Production Architecture...")
        create_production_architecture()
        print("✅ Production architecture: architecture_production.png + .svg")
        
        print("\n🔄 Creating Data Flow Diagram...")
        create_data_flow_diagram()
        print("✅ Data flow: data_flow.png + .svg")
        
        print("\n🛠️ Creating Technology Stack...")
        create_technology_stack_diagram()
        print("✅ Technology stack: technology_stack.png + .svg")
        
        print("\n🚀 Creating Deployment Options...")
        create_deployment_diagram()
        print("✅ Deployment options: deployment_options.png + .svg")
        
        print("\n🎉 ALL DIAGRAMS GENERATED SUCCESSFULLY!")
        print("\n📁 Files created (PNG + SVG, 300 DPI):")
        print("   - architecture_local.png/.svg")
        print("   - architecture_production.png/.svg") 
        print("   - data_flow.png/.svg")
        print("   - technology_stack.png/.svg")
        print("   - deployment_options.png/.svg")
        print("\n🎯 ZERO ERRORS - All connections properly mapped!")
        print("📊 HIGH QUALITY - 300 DPI with professional styling!")
        print("🎨 DUAL FORMAT - Both PNG and SVG versions created!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()