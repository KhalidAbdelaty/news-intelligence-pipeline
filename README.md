# 📰 News Intelligence Pipeline

[![Python 3.11.9](https://img.shields.io/badge/python-3.11.9-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-ready-orange.svg)](https://aws.amazon.com/)
[![Azure](https://img.shields.io/badge/Azure-ready-blue.svg)](https://azure.microsoft.com/)

> **A constraint-based data engineering pipeline that proves complex problems don't need complex solutions**

Real-time news intelligence with sentiment analysis, trending topics, and interactive analytics. Built in exactly 5 files to demonstrate clean architecture principles.

## 🎯 **The Challenge**

Can you build a production-grade data pipeline in just 5 files? This project proves it's not only possible, but the constraint actually leads to better engineering.

## 🏗️ **Architecture**

### **System Overview**
![System Architecture](docs/architecture_local.png)

### **Data Flow**
![Data Flow](docs/data_flow.png)

### **Production Deployment**
![Production Architecture](docs/architecture_production.png)

## ⚡ **Quick Start**

### **Local Development**
```bash
git clone https://github.com/yourusername/news-intelligence-pipeline.git
cd news-intelligence-pipeline

python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

export GNEWS_API_KEY="your_api_key_here"
streamlit run dashboard.py
```

### **Docker (Recommended)**
```bash
docker-compose up --build
```
Access at: `http://localhost:8501`

## 📊 **What It Does**

- **📡 Real-time Ingestion**: Fetches from 60,000+ news sources
- **🧠 Sentiment Analysis**: Advanced NLP with confidence scoring
- **🔥 Trending Topics**: Temporal analysis and velocity tracking
- **📈 Interactive Analytics**: Streamlit dashboard with Plotly charts
- **⚡ Quality Monitoring**: Comprehensive data validation
- **🔄 Real-time Updates**: Live dashboard with auto-refresh

## 🛠️ **The 5-File Architecture**

| File | Purpose | Lines |
|------|---------|-------|
| `config.py` | Settings, monitoring, health checks | ~400 |
| `ingest.py` | Real-time data fetching with retry logic | ~600 |
| `transform.py` | NLP processing and sentiment analysis | ~800 |
| `storage.py` | Database operations with quality tracking | ~700 |
| `dashboard.py` | Interactive Streamlit interface | ~1000 |

**Total: ~3,500 lines of clean, production-ready Python**

## 🚀 **Cloud Deployment**

### **AWS (One-Click)**
```bash
# Using AWS App Runner
aws apprunner create-service --cli-input-json file://aws-config.json
```

### **Azure Container Instances**
```bash
az container create --resource-group myResourceGroup \
  --name news-intelligence \
  --image news-intelligence:latest \
  --environment-variables GNEWS_API_KEY=your_key
```

### **Google Cloud Run**
```bash
gcloud run deploy --image gcr.io/project/news-intelligence \
  --set-env-vars GNEWS_API_KEY=your_key
```

## 📈 **Performance**

- **Processing Speed**: 50+ articles/second
- **Memory Usage**: <200MB typical operation
- **API Efficiency**: 95%+ success rate
- **Database**: Optimized for 1M+ articles
- **Scalability**: Tested with 100K+ articles

## 🎓 **Use Cases**

- **Brand Monitoring**: Track mentions and sentiment
- **Market Intelligence**: Monitor industry trends
- **Crisis Management**: Early negative sentiment detection
- **Content Strategy**: Identify trending topics
- **Competitive Analysis**: Track competitor coverage

## 🔧 **Technology Stack**

![Technology Stack](docs/technology_stack.png)

- **Backend**: Python 3.11.9, SQLite/PostgreSQL
- **Frontend**: Streamlit, Plotly
- **NLP**: TextBlob, Custom algorithms
- **Infrastructure**: Docker, GitHub Actions
- **Cloud**: AWS, Azure, GCP ready

## 📊 **Dashboard Features**

- **Real-time Metrics**: Live article processing stats
- **Sentiment Analysis**: Interactive charts and trends
- **Quality Monitoring**: Data validation reports
- **Source Comparison**: Multi-source analytics
- **Search & Filter**: Advanced article discovery
- **Export Options**: CSV, JSON data export

## 🧪 **Testing**

```bash
# Run all tests
python -m pytest tests/

# Code quality
black --check *.py
flake8 *.py

# Security scan
bandit -r *.py
```

## 📚 **Documentation**

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[API Reference](docs/api.md)** - Complete API documentation
- **[Deployment Guide](docs/deployment.md)** - Cloud deployment options
- **[Configuration](docs/configuration.md)** - Environment settings

## 🎨 **Architecture Diagrams**

All diagrams available in PNG and SVG formats:

- [Local Development](docs/architecture_local.svg)
- [Production Deployment](docs/architecture_production.svg)
- [Data Flow](docs/data_flow.svg)
- [Technology Stack](docs/technology_stack.svg)
- [Deployment Options](docs/deployment_options.svg)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

MIT License - see [LICENSE](LICENSE) for details.

## 🏆 **Why This Matters**

This project demonstrates that:
- **Constraints drive creativity**, not limit it
- **Simple architectures** can solve complex problems
- **Clean code** is more valuable than clever code
- **Production-ready** doesn't mean complicated

## 👨‍💻 **Author**

**Khalid Abdelaty**  
*AWS Community Builder & Data Engineer*

- 💼 [LinkedIn](https://linkedin.com/in/khalidabdelaty)
- 🐙 [GitHub](https://github.com/KhalidAbdelaty)
- 📧 khalidabdelatty80@gmail.com
- 🏆 AWS Certified Data Engineer

---

<div align="center">
  <strong>⭐ If this project helped you, please star it! ⭐</strong>
  <br>
  <em>Built with constraints, deployed with confidence</em>
</div>
