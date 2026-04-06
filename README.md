# Olive Soft Prospecting - Job Scoring System

Production-grade semantic job scoring and opportunity detection system for identifying high-quality consulting opportunities.

![Status](https://img.shields.io/badge/status-production%20ready-success)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-proprietary-red)

---

## Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Virtual environment

### Installation

```bash
# 1. Clone and setup
git clone <your-repo>
cd prototypePFE

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements_production.txt

# 4. Download NLP model
python -m spacy download fr_core_news_sm

# 5. Start API
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

# 6. Test (in new terminal)
python test_api.py
```

**API is now running at:** http://localhost:8000

---

## What's Inside

### 🎯 Core System

- **api.py** - FastAPI REST service (ready for n8n)
- **scoring_engine.py** - 6-dimensional scoring engine
- **feature_extractor.py** - Advanced NLP feature extraction
- **config_production.py** - Centralized configuration

### 📚 Documentation

| Document | Purpose |
|----------|---------|
| **IMPLEMENTATION_SUMMARY.md** | Complete overview (START HERE) |
| **ANALYSIS_AND_RECOMMENDATIONS.md** | Detailed analysis of improvements |
| **N8N_INTEGRATION_GUIDE.md** | How to integrate with n8n |
| **DEPLOYMENT_GUIDE.md** | Production deployment options |

### 🧪 Testing

```bash
# Run test suite
python test_api.py

# With performance benchmark
python test_api.py --benchmark
```

---

## API Usage

### Single Job Scoring

```bash
curl -X POST "http://localhost:8000/score" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior ML Engineer",
    "description": "Join our AI team. Experience with Python, PyTorch, NLP required...",
    "company": "TechCorp",
    "location": "Paris"
  }'
```

### Response

```json
{
  "success": true,
  "final_score": 0.845,
  "dimensions": {
    "skill_matching": 0.90,
    "consulting_fit": 0.65,
    "seniority_match": 0.95,
    "semantic_relevance": 0.82,
    "growth_potential": 0.70,
    "cultural_alignment": 0.75
  },
  "reasons": [
    "Strong skill match: Python, NLP, PyTorch",
    "Perfect seniority match (Senior)"
  ],
  "skills_detected": ["python", "nlp", "pytorch"],
  "seniority": "senior"
}
```

### Full Documentation

Visit: **http://localhost:8000/docs** (Swagger UI)

---

## Scoring Dimensions (6)

The system scores jobs across 6 dimensions:

| Dimension | Weight | Measures |
|-----------|--------|----------|
| **Skill Matching** | 25% | CV skill matches |
| **Consulting Fit** | 20% | Advisory/strategy indicators |
| **Seniority Match** | 15% | Job level alignment |
| **Semantic Relevance** | 20% | Content similarity |
| **Growth Potential** | 10% | Emerging tech (LLMs, AI) |
| **Cultural Alignment** | 10% | Work mode, company fit |

Weights are configurable for different strategies:
- Default: Balanced across all dimensions
- Consulting Mode: 35% weight on consulting fit

---

## Key Features

✨ **Production-Ready**
- Comprehensive error handling
- Input validation (Pydantic schemas)
- Health check endpoint
- Logging and monitoring

🚀 **Scalable**
- Batch processing support
- Batch embeddings (efficient)
- Async-ready architecture
- Can score 500+ jobs

🎯 **Consulting-Optimized**
- Prestige firm detection (McKinsey, BCG, etc.)
- Strategic keyword weighting
- Consulting-focused scoring mode

📊 **Explainable**
- Human-readable match reasons
- Feature breakdown
- Dimension scores
- Skills detected

🔌 **n8n Ready**
- REST API with JSON
- Batch endpoints
- Standard error responses
- Fast response times (<2s)

---

## Architecture

```
n8n Workflow
    ↓
  API (FastAPI)
    ↓
Scoring Engine (6 dimensions)
    ↓
Feature Extraction
    ├─ Skill matching (fuzzy)
    ├─ Seniority detection
    ├─ Consulting signals
    └─ Emerging tech
    ↓
Embedding Models (SentenceTransformers)
```

---

## Files

```
prototypePFE/
├── IMPLEMENTATION_SUMMARY.md          ← Start here
├── ANALYSIS_AND_RECOMMENDATIONS.md
├── N8N_INTEGRATION_GUIDE.md
├── DEPLOYMENT_GUIDE.md
├── README.md                          ← This file
│
├── api.py                             ← REST API (FastAPI)
├── scoring_engine.py                  ← 6D scoring logic
├── feature_extractor.py               ← NLP feature extraction
├── api_models.py                      ← Pydantic schemas
├── config_production.py               ← Configuration
├── utils.py                           ← Helper utilities
│
├── test_api.py                        ← Test suite
├── requirements_production.txt         ← Dependencies
│
├── config.py                          ← Original config
├── main.py                            ← Original script
├── preprocessing.py                   ← Original preprocessing
├── scoring.py                         ← Original scoring
│
└── job-scrapping - Jobs.csv           ← Sample data
```

---

## Configuration

Edit **config_production.py** to customize:

```python
# Add/modify CV skills (with importance weights)
CV_SKILLS = {
    "python": 3,           # High importance
    "machine learning": 3,
    "sql": 2,             # Medium importance
    # ...
}

# Adjust scoring weights
SCORING_WEIGHTS = {
    "skill_matching": 0.25,
    "consulting_fit": 0.20,
    # ... (must sum to 1.0)
}

# Set target seniority (Senior, Mid-level, Junior, etc.)
TARGET_SENIORITY = "senior"
```

---

## Performance

| Operation | Time |
|-----------|------|
| Single job scoring | ~1.5-2.0s |
| Batch 20 jobs | ~3-5s |
| Batch 100 jobs | ~20-30s |
| Health check | <100ms |

**Throughput:** 1,800+ jobs/hour

---

## n8n Integration

### Pattern 1: Real-Time Scoring

```
Webhook (job posted)
  → HTTP POST /score
  → Filter by threshold
  → Save result
```

### Pattern 2: Bulk CSV Import

```
Read CSV file
  → Split into batches
  → HTTP POST /score/batch
  → Rank results
  → Export to Sheets
```

### Pattern 3: Scheduled Scraping

```
Trigger (daily at 6am)
  → Scrape LinkedIn/Indeed
  → Score batch
  → Generate report
  → Email stakeholders
```

See **N8N_INTEGRATION_GUIDE.md** for complete examples.

---

## Consulting Mode

For targeting consulting opportunities specifically:

```bash
curl -X POST "http://localhost:8000/score?consulting_mode=true" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

In consulting mode:
- Consulting fit weight: 35% (vs 20% default)
- Prestige firms get a boost
- Strategic skills valued higher

---

## Troubleshooting

### API won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list | grep -E "fastapi|sentence"

# Try reinstalling
pip install -r requirements_production.txt --force-reinstall
```

### Slow responses
```bash
# Check CPU usage
top  # Linux/Mac
# Task Manager on Windows

# Enable GPU if available
# Models will auto-detect CUDA

# Check models loaded
curl http://localhost:8000/health
```

### Models not found
```bash
# Download NLP model
python -m spacy download fr_core_news_sm

# Verify
python -c "import spacy; nlp = spacy.load('fr_core_news_sm'); print('OK')"
```

---

## Deployment

### Development
```bash
python -m uvicorn api:app --reload
```

### Production

**Option 1: Docker**
```bash
docker build -t olive-scoring .
docker run -p 8000:8000 olive-scoring
```

**Option 2: Systemd (Linux)**
```bash
# Create service file
sudo systemctl enable olive-scoring
sudo systemctl start olive-scoring
```

**Option 3: Gunicorn**
```bash
gunicorn --workers 4 -k uvicorn.workers.UvicornWorker api:app
```

See **DEPLOYMENT_GUIDE.md** for complete instructions.

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Service health check |
| GET | /docs | Swagger UI documentation |
| GET | /config | Current scoring configuration |
| POST | /score | Score single job |
| POST | /score/batch | Score multiple jobs |
| POST | /demo | Try with example job |

---

## Response Format

**Success Response:**
```json
{
  "success": true,
  "final_score": 0.845,
  "match_percentage": 0.845,
  "dimensions": { /* 6 scores */ },
  "reasons": ["Reason 1", "Reason 2"],
  "skills_detected": ["skill1", "skill2"],
  "seniority": "senior",
  "is_consulting_opportunity": false
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Description too short",
  "final_score": 0,
  "match_percentage": 0.0
}
```

---

## Advanced Usage

### Filter Results
```python
from utils import ScoringResultRanker

# Top scores
ranked = ScoringResultRanker.rank_by_score(results)

# Above threshold
high_quality = ScoringResultRanker.filter_by_threshold(results, 0.75)

# With specific skills
with_python = ScoringResultRanker.filter_by_skill(results, ["python"])

# Consulting only
consulting = ScoringResultRanker.filter_consulting_only(results)
```

### Export Results
```python
from utils import ScoreExporter

# CSV
csv = ScoreExporter.to_csv_compatible(results)

# JSON
json_str = ScoreExporter.to_json(results, pretty=True)

# Markdown report
report = ScoreExporter.to_markdown_report(results)
```

---

## What's New vs Original

| Aspect | Before | After |
|--------|--------|-------|
| **API** | None | FastAPI REST |
| **Dimensions** | 3 | 6 (with consulting focus) |
| **Seniority** | Not detected | Full classification |
| **Explainability** | Black box | Detailed reasons |
| **Consulting** | Generic | Prestige detection |
| **Errors** | Crashes | Graceful handling |
| **Scalability** | Single job | Batch ready |

---

## Next Steps

1. **Test locally**: Run `python test_api.py`
2. **Read docs**: See IMPLEMENTATION_SUMMARY.md
3. **Configure**: Update config_production.py
4. **Integrate n8n**: Follow N8N_INTEGRATION_GUIDE.md
5. **Deploy**: Follow DEPLOYMENT_GUIDE.md

---

## Support

- **Documentation**: See markdown files in this directory
- **API Docs**: http://localhost:8000/docs (when running)
- **Issues**: Check DEPLOYMENT_GUIDE.md troubleshooting
- **Community**: n8n forum for n8n-specific questions

---

## License

Proprietary - Olive Soft Prospecting

---

## Version

**v1.0.0** - Production-Ready MVP

**Last Updated:** 2024

---

## Quick Reference

```bash
# Start development
python -m uvicorn api:app --reload

# Run tests
python test_api.py

# Try API
curl http://localhost:8000/demo

# View docs
# Open: http://localhost:8000/docs

# Run benchmarks
python test_api.py --benchmark

# Update configuration
# Edit: config_production.py
# Restart API

# Deploy to production
# See: DEPLOYMENT_GUIDE.md
```

---

**Ready to identify premium job opportunities! 🚀**

For detailed information, see **IMPLEMENTATION_SUMMARY.md**

