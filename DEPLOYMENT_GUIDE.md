# DEPLOYMENT & QUICK START GUIDE

## Quick Start (Development)

### 1. Set up Python environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements_production.txt
```

### 3. Download NLP Model

```bash
python -m spacy download fr_core_news_sm
```

### 4. Start the API

```bash
# Development (with auto-reload)
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production (no reload)
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Verify it's running

```bash
# Health check
curl http://localhost:8000/health

# Open API docs
# Visit: http://localhost:8000/docs
```

### 6. Test scoring

```bash
# Test with curl
curl -X POST "http://localhost:8000/demo" \
  -H "Content-Type: application/json"

# Or test on http://localhost:8000/docs (Swagger UI)
```

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│        n8n Workflow / External App       │
└────────────────────┬────────────────────┘
                     │
                     ↓ HTTP/JSON
        ┌────────────────────────────┐
        │   FastAPI Application      │
        │   (api.py)                 │
        │ - /score                   │
        │ - /score/batch             │
        │ - /health                  │
        └────────┬───────────────────┘
                 │
                 ↓
    ┌────────────────────────────────┐
    │  Scoring Engine (6 dimensions)  │
    │  (scoring_engine.py)            │
    │                                 │
    │  - Skill Matching (25%)          │
    │  - Consulting Fit (20%)          │
    │  - Seniority Match (15%)         │
    │  - Semantic Relevance (20%)      │
    │  - Growth Potential (10%)        │
    │  - Cultural Alignment (10%)      │
    └────────┬─────────────────────────┘
             │
    ┌────────┴─────────────────────────┐
    │                                   │
    ↓                                   ↓
┌───────────────────────┐    ┌────────────────────┐
│ Feature Extraction     │    │ Embedding Models    │
│ (feature_extractor.py) │    │ (SentenceTransf.)   │
│                        │    │                     │
│ - Skill extraction     │    │ - Bi-encoder        │
│ - Seniority detection  │    │ - Semantic scoring  │
│ - Consulting signals   │    │                     │
│ - Emerging tech        │    │ Device: CPU/GPU     │
└────────────────────────┘    └──────────────────────┘

Configuration:
        ↓
    config_production.py
    - CV skills (weighted)
    - Scoring weights
    - Consulting keywords
    - Thresholds
```

---

## Production Deployment Options

### Option A: Linux Systemd + Gunicorn

**Setup:**
1. SSH to Linux server
2. Clone repository
3. Create virtualenv
4. Install dependencies
5. Create systemd service file
6. Enable and start

**Installation Script:**
```bash
#!/bin/bash

# Install system dependencies
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip

# Create app directory
sudo mkdir -p /opt/olive-scoring
cd /opt/olive-scoring

# Clone code
sudo git clone <YOUR_REPO> .

# Create virtualenv
python3.10 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements_production.txt
pip install gunicorn

# Download NLP model
python -m spacy download fr_core_news_sm

# Create systemd service
sudo tee /etc/systemd/system/olive-scoring.service > /dev/null <<EOF
[Unit]
Description=Olive Soft Job Scoring API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/olive-scoring
Environment="PATH=/opt/olive-scoring/venv/bin"
ExecStart=/opt/olive-scoring/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    api:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable olive-scoring
sudo systemctl start olive-scoring

# Check status
sudo systemctl status olive-scoring

# View logs
sudo journalctl -u olive-scoring -f
```

---

### Option B: Docker Container

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_production.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_production.txt

# Download NLP model
RUN python -m spacy download fr_core_news_sm

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Run with gunicorn
CMD ["gunicorn", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "api:app"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  olive-scoring:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
      - WORKERS=4
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

**Deploy:**
```bash
docker-compose up -d
docker-compose logs -f
docker-compose ps
```

---

### Option C: Kubernetes

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: olive-scoring
  labels:
    app: olive-scoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: olive-scoring
  template:
    metadata:
      labels:
        app: olive-scoring
    spec:
      containers:
      - name: api
        image: your-registry/olive-scoring:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: olive-scoring
spec:
  selector:
    app: olive-scoring
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Configuration Management

### 1. Update CV Skills

Edit `config_production.py`:
```python
CV_SKILLS = {
    "python": 3,
    "machine learning": 3,
    # ... add/modify skills
}
```

Restart API for changes to apply.

### 2. Adjust Scoring Weights

Edit `config_production.py`:
```python
SCORING_WEIGHTS = {
    "skill_matching": 0.25,
    "consulting_fit": 0.20,
    # ... modify weights (must sum to 1.0)
}
```

### 3. Change Target Seniority

Edit `config_production.py`:
```python
TARGET_SENIORITY = "senior"  # or "mid-level", "junior", etc.
```

---

## Monitoring & Maintenance

### Health Monitoring

```bash
# Check health regularly
while true; do
    curl -s http://localhost:8000/health | jq .
    sleep 60
done
```

### Log Monitoring (Docker)

```bash
docker logs -f olive-scoring
```

### Memory Usage

```bash
# Monitor container memory
docker stats olive-scoring

# Or on Linux
ps aux | grep uvicorn
free -h
```

### Performance Tuning

**If API is slow:**
1. Add more workers: `--workers 8` (Gunicorn)
2. Enable GPU support (if available)
3. Reduce model size

**If memory high:**
1. Reduce number of workers
2. Set memory limits
3. Implement model caching cleanup

---

## Scaling Strategy

### Single Server (MVP)
- 1 API instance
- Single machine
- 50-100 jobs/minute

### Multi-Instance (Growth)
```
Load Balancer (nginx)
    ↓
    ├─→ API Instance 1 (port 8001)
    ├─→ API Instance 2 (port 8002)
    └─→ API Instance 3 (port 8003)
```

**Setup:**
```nginx
upstream olive_scoring {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    location / {
        proxy_pass http://olive_scoring;
    }
}
```

### Kubernetes (Enterprise)
- Multiple replicas
- Auto-scaling
- Health monitoring
- Rolling updates

---

## Troubleshooting

### API won't start

```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list

# Try importing modules
python -c "import fastapi; import sentence_transformers; print('OK')"

# Check port is free
lsof -i :8000
```

### Slow responses

```bash
# Check CPU usage
top

# Check memory
free -h

# Check GPU (if using)
nvidia-smi

# Monitor logs
tail -f /var/log/olive-scoring.log
```

### "Models not loaded" error

```bash
# Verify spacy model
python -c "import spacy; nlp = spacy.load('fr_core_news_sm'); print('OK')"

# Reinstall if needed
python -m spacy download fr_core_news_sm --force
```

### Port already in use

```bash
# On Linux/Mac
lsof -i :8000
kill -9 <PID>

# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Updating the System

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install --upgrade -r requirements_production.txt

# Download latest NLP model
python -m spacy download fr_core_news_sm --force

# Restart service
sudo systemctl restart olive-scoring

# Or Docker
docker-compose down
docker-compose pull
docker-compose up -d
```

---

## Backup & Recovery

```bash
# Backup configuration
cp config_production.py config_production.py.bak
cp config_production.py ~/backups/config_$(date +%Y%m%d).py

# Restore if needed
cp ~/backups/config_YYYYMMDD.py config_production.py
systemctl restart olive-scoring
```

---

## Next Steps

1. ✅ Deploy to development environment
2. ✅ Test with your CV and sample jobs
3. ✅ Integrate with n8n (see N8N_INTEGRATION_GUIDE.md)
4. ✅ Monitor performance metrics
5. ✅ Deploy to production
6. ✅ Set up monitoring and alerts

