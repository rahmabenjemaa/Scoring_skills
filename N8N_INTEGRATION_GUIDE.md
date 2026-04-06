# N8N INTEGRATION GUIDE - Olive Soft Job Scoring System

## Table of Contents
1. [Quick Start](#quick-start)
2. [API Overview](#api-overview)
3. [N8N Integration Examples](#n8n-integration-examples)
4. [Workflow Design Patterns](#workflow-design-patterns)
5. [Error Handling](#error-handling)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Start the Scoring API

```bash
# Install dependencies
pip install -r requirements_production.txt

# Download French NLP model
python -m spacy download fr_core_news_sm

# Start API server
python -m uvicorn api:app --host 0.0.0.0 --port 8000

# Verify it's running
curl http://localhost:8000/health
```

API will be available at: `http://localhost:8000`
API documentation (Swagger): `http://localhost:8000/docs`

---

## API Overview

### Endpoint 1: Health Check
```
GET /health
```

**Purpose:** Verify API is running and models are loaded

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Endpoint 2: Score Single Job
```
POST /score
```

**Request:**
```json
{
  "title": "Senior ML Engineer",
  "description": "We're looking for a Senior ML Engineer with 5+ years experience in NLP...",
  "company": "TechCorp AI",
  "location": "Paris",
  "source": "LinkedIn",
  "consulting_mode": false
}
```

**Response:**
```json
{
  "success": true,
  "final_score": 0.845,
  "match_percentage": 0.845,
  "dimensions": {
    "skill_matching": 0.90,
    "consulting_fit": 0.65,
    "seniority_match": 0.95,
    "semantic_relevance": 0.82,
    "growth_potential": 0.70,
    "cultural_alignment": 0.75
  },
  "reasons": [
    "Strong skill match: Python, NLP, transformers",
    "Perfect seniority match (Senior)",
    "Cutting-edge opportunity: llm, gpt"
  ],
  "top_reason": "Strong skill match: Python, NLP, transformers",
  "skills_detected": ["python", "nlp", "transformers"],
  "seniority": "senior",
  "is_consulting_opportunity": false,
  "prestige_firm": null,
  "emerging_technologies": ["llm", "gpt"]
}
```

### Endpoint 3: Batch Scoring
```
POST /score/batch
```

**Request:**
```json
{
  "jobs": [
    {
      "title": "Senior ML Engineer",
      "description": "...",
      "company": "Company1"
    },
    {
      "title": "AI Consultant",
      "description": "...",
      "company": "Company2"
    }
  ],
  "use_consulting_mode": false
}
```

**Response:**
```json
{
  "success": true,
  "total_jobs": 2,
  "successful_scores": 2,
  "failed_scores": 0,
  "average_score": 0.82,
  "results": [
    { /* individual results */ }
  ]
}
```

---

## N8N Integration Examples

### Pattern 1: Simple Single Job Scoring

**N8N Workflow:**
1. **Trigger**: Webhook or Web Request
2. **HTTP Request** node:
   - Method: POST
   - URL: `http://localhost:8000/score`
   - Body:
     ```json
     {
       "title": "{{ $json.job_title }}",
       "description": "{{ $json.job_description }}",
       "company": "{{ $json.company }}",
       "location": "{{ $json.location }}"
     }
     ```
3. **Set**: Filter/transform results
4. **Output**: Return score

---

### Pattern 2: Process CSV file

**N8N Workflow:**
1. **Trigger**: File uploaded to folder
2. **Read CSV file** → Extract rows
3. **Loop**: For each job row
   - **HTTP Request** to `/score`
   - **Save result** to database/sheet
4. **Aggregate**: Create summary
5. **Notify**: Send report via email

**Test Data Structure in CSV:**
```
title,description,company,location,source
Senior Machine Learning Engineer,"Design and build ML systems for enterprise clients...",TechCorp,Paris,LinkedIn
AI Consultant,"Work with Fortune 500 clients on AI transformation...","McKinsey","New York",LinkedIn
```

---

### Pattern 3: LinkedIn Job Scraper Integration

**N8N Workflow:**
1. **Trigger**: Scheduled (daily)
2. **Scrape LinkedIn jobs** (using web scraper or API)
3. **Split batch** into chunks (for efficiency)
4. **HTTP Request** to `/score/batch`
   ```json
   {
     "jobs": "{{ $json.jobs }}",
     "use_consulting_mode": true
   }
   ```
5. **Map results** for ranking:
   ```javascript
   $json.results.map(r => ({
     name: r.title,
     score: r.final_score,
     reason: r.top_reason,
     consulting: r.is_consulting_opportunity
   }))
   ```
6. **Save top 50** to database
7. **Send alerts** for scores > 0.8

---

### Pattern 4: Real-time HTTP API for n8n

**Use Case:** n8n calls your scoring API for each job as it scrapes

**N8N Configuration:**

```
Node Type: HTTP Request
Method: POST
URL: http://localhost:8000/score
Authentication: None (for MVP)
Content-Type: application/json

Body:
{
  "title": "{{ $json.title }}",
  "description": "{{ $json.description }}",
  "company": "{{ $json.company }}",
  "location": "{{ $json.location }}",
  "consulting_mode": false
}

Response mapping:
- Score: response.final_score
- Seniority: response.seniority
- Reason: response.top_reason
- Skills: response.skills_detected
```

### Pattern 5: Filtering and Conditionals

**N8N Workflow with Filtering:**

```
1. Score job with HTTP Request
2. Conditional node:
   - If score >= 0.75:
     - Add to "High Priority" bucket
     - Notify hiring manager
   - Else if score >= 0.50:
     - Add to "Review Later" bucket
   - Else:
     - Archive
```

---

## Workflow Design Patterns

### Pattern A: Single-Job Real-Time Scoring

**Use when:** Scoring jobs one at a time (e.g., real-time webhook)

```
Job Input → HTTP /score → Filter by threshold → Store/Notify
```

**Pros:**
- Low latency
- Real-time feedback
- Simple error handling

**Cons:**
- Slower for bulk operations
- Higher API load

---

### Pattern B: Batch Processing (CSV Import)

**Use when:** Processing 10-100 jobs from file

```
Read CSV → Group into batches → HTTP /score/batch → Aggregate → Export
```

**Pros:**
- Faster overall
- Good for bulk imports
- Efficient resource usage

**Cons:**
- Requires batch-friendly file format

---

### Pattern C: Scheduled Bulk Job

**Use when:** Daily/weekly scraping and scoring

```
Trigger (Schedule) → Scrape platform → Score batch → Rank → Save → Report
```

**Configuration:**
- Trigger: Every day at 6 AM
- Scrape: LinkedIn, Indeed, Glassdoor
- Score: Use `/score/batch` with consulting_mode=true
- Rank: Sort by `final_score` descending
- Save: To PostgreSQL or Google Sheets
- Report: Email top 10

---

## Error Handling

### Common Errors

**1. Empty Description**
```json
{
  "success": false,
  "error": "Description too short",
  "final_score": 0,
  "match_percentage": 0.0
}
```

**N8N Handling:**
```javascript
// Skip jobs with scores = 0
if ($json.final_score > 0) {
  return $json;
} else {
  return null;
}
```

---

**2. API Connection Lost**
```json
{
  "success": false,
  "error": "Failed to connect to scoring service"
}
```

**N8N Handling:**
```javascript
// Retry logic (n8n native retry)
// Set on HTTP node: "Retry on Error" = 3 times
```

---

**3. Malformed Input**
```json
{
  "success": false,
  "error": "Invalid request schema"
}
```

**N8N Handling:** Validate before sending
```javascript
if (!$json.title || !$json.description) {
  return { error: "Missing required fields" };
}
```

---

## Performance Optimization

### 1. Batch Processing Strategy

**For 500+ jobs:**

- **Batch size:** 20 jobs per request (1-2 seconds per batch)
- **Total time:** ~50-100 requests = 50-200 seconds

**N8N Implementation:**
```javascript
// Loop pagination
const batchSize = 20;
const batches = [];
for (let i = 0; i < jobs.length; i += batchSize) {
  batches.push(jobs.slice(i, i + batchSize));
}
// Loop through batches and score
```

### 2. Parallel Scoring

**Use n8n's Split node to parallelize:**

1. Split jobs into 4 parallel branches
2. Each branch scores 25% of jobs
3. Merge results

**Expected improvement:** 2-3x faster

### 3. Caching

**For repeated jobs (to prevent re-scoring):**

```javascript
// Store hash of (title + description) → score
// Check cache before API call
// TTL: 24 hours
```

---

### 4. API Response Time Targets

| Operation | Target Time | Notes |
|-----------|------------|-------|
| Single job scoring | < 2 seconds | Including model inference |
| Batch 20 jobs | < 5 seconds | Parallel processing |
| Batch 100 jobs | < 30 seconds | Consider splitting |
| Health check | < 100ms | Quick verification |

---

## Troubleshooting

### Issue 1: "Models not loaded"

**Solution:**
```bash
# Download required NLP model
python -m spacy download fr_core_news_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('fr_core_news_sm'); print('OK')"
```

---

### Issue 2: Slow API responses

**Solutions:**
1. Check GPU availability: `nvidia-smi`
2. Reduce batch size
3. Enable CPU optimization in PyTorch
4. Use consulting_mode=false (lighter scoring)

---

### Issue 3: High memory usage

**Solutions:**
1. Restart API hourly (in production)
2. Disable logging in scoring engine
3. Use smaller embedding models
4. Process jobs in smaller batches

---

### Issue 4: Inconsistent scores

**This is normal!** Semantic models have small variance.

**Solution:**
- For critical decisions: Score 2-3 times, average the results
- Accept ±0.05 score variation as normal

---

## Production Deployment

### Option 1: Docker (Recommended)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements_production.txt .
RUN pip install -r requirements_production.txt
RUN python -m spacy download fr_core_news_sm

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Run:**
```bash
docker build -t olive-scoring .
docker run -p 8000:8000 olive-scoring
```

---

### Option 2: Systemd Service (Linux)

Create `/etc/systemd/system/olive-scoring.service`:
```ini
[Unit]
Description=Olive Soft Job Scoring API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/olive-scoring
ExecStart=/opt/olive-scoring/venv/bin/python -m uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable:**
```bash
sudo systemctl enable olive-scoring
sudo systemctl start olive-scoring
```

---

## Best Practices

1. **Always check /health before processing**
   - Verify models are loaded

2. **Implement retry logic**
   - Network errors are transient

3. **Use consulting_mode wisely**
   - Default: false
   - Set to true when specifically targeting consulting roles

4. **Monitor API performance**
   - Track average response time
   - Alert if > 5 seconds per job

5. **Update CV skills regularly**
   - Edit `config_production.py`
   - Restart API to apply changes

6. **Implement result caching**
   - Avoid re-scoring identical jobs

7. **Use batch endpoints for bulk work**
   - More efficient than individual requests

---

## Support

**For issues:**
1. Check `/docs` endpoint for API documentation
2. Review responses in n8n workflow execution
3. Check API logs for errors
4. Verify input data format matches schema

