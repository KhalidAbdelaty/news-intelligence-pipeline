# 📦 Installation Guide

## Prerequisites

- Python 3.11.9 (exactly)
- Git
- GNews API key (free from [gnews.io](https://gnews.io))

## Local Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/news-intelligence-pipeline.git
cd news-intelligence-pipeline
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Setup
```bash
# Windows
set GNEWS_API_KEY=your_api_key_here
set ENVIRONMENT=development

# Linux/Mac
export GNEWS_API_KEY=your_api_key_here
export ENVIRONMENT=development
```

### 5. Run Application
```bash
streamlit run dashboard.py
```

Access at: `http://localhost:8501`

## Docker Installation

### 1. Using Docker Compose (Recommended)
```bash
git clone https://github.com/yourusername/news-intelligence-pipeline.git
cd news-intelligence-pipeline

# Set environment variables in .env file
echo "GNEWS_API_KEY=your_api_key_here" > .env

docker-compose up --build
```

### 2. Using Docker directly
```bash
docker build -t news-intelligence .
docker run -p 8501:8501 -e GNEWS_API_KEY=your_key news-intelligence
```

## Verification

1. Open `http://localhost:8501`
2. Click "Run Enhanced Pipeline"
3. Verify articles are fetched and processed
4. Check dashboard shows sentiment analysis

## Troubleshooting

### Python Version Issues
```bash
python --version  # Must be 3.11.9
```

### API Key Issues
- Verify key is valid at [gnews.io](https://gnews.io)
- Check environment variable is set
- Ensure no extra spaces in key

### Port Conflicts
```bash
# Use different port
streamlit run dashboard.py --server.port 8502
```

### Dependencies Issues
```bash
# Clear cache and reinstall
pip cache purge
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```
