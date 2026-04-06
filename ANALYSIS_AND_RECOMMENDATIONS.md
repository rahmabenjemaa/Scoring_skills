# Olive Soft Prospecting - Job Scoring System Analysis

## 1. ANALYSIS OF CURRENT SCORING SYSTEM

### 1.1 Algorithm Overview

Your system implements a **three-stage hybrid scoring approach**:

#### Stage 1: Structured Feature Engineering
- **Spacy-based skill extraction** with EntityRuler patterns
- Detects skills from the CV skill dictionary in job text
- Calculates **weighted coverage** (which CV skills appear in job)
- Computes **frequency score** (how many times each skill appears)
- Applies **title boost** (double-weight if skill appears in job title)
- Result: Normalized score 0-1

#### Stage 2: Semantic Retrieval (Bi-Encoder)
- Uses `sentence-transformers/all-MiniLM-L6-v2` to encode CV and job text
- Computes cosine similarity between embeddings
- Efficient batch processing (vectorized operations)
- Result: Semantic score 0-1

#### Stage 3: Cross-Encoder Re-Ranking
- Uses `cross-encoder/ms-marco-MiniLM-L-6-v2` for fine-grained relevance
- Processes top-20 candidates from stage 2
- Provides more nuanced relevance than pure embeddings
- Result: Cross score 0-1 (normalized per batch)

#### Final Score
```
final_score = 0.4 * skill_score + 0.3 * semantic_score + 0.3 * cross_score
```

---

### 1.2 STRENGTHS

✅ **Strong architectural foundation**
- Multi-stage design: retrieval → reranking → ranking
- Combines symbolic (skills) + semantic (embeddings) approaches
- Batch processing for performance

✅ **Production-ready components**
- Spacy NLP integration for structured extraction
- Efficient batch embeddings with SentenceTransformers
- Pre-filtering mechanism to eliminate low-quality jobs

✅ **Normalized scoring**
- All components normalized to 0-1 range
- Allows fair weighting across different scales

✅ **French language support**
- Loads `fr_core_news_sm` for French text processing

---

### 1.3 IDENTIFIED WEAKNESSES & PROBLEMS

❌ **1. Limited Explainability**
- Final score is a black box
- No indication of *why* a job matches (which skills? which semantic themes?)
- Missing reasoning for non-technical stakeholders

❌ **2. Crude Pre-Filtering**
- Only checks if source contains "indeed"
- Ignores all other job sources (LinkedIn, Glassdoor, etc.)
- No filtering for irrelevant job types (internships, contracts)

❌ **3. No Seniority Detection**
- CV is "Senior profiles" but scored equally for Junior roles
- Missing seniority-based filtering/weighting

❌ **4. Static Skill Weights**
- Hardcoded weights don't reflect business priorities
- No mechanism to adjust weights based on hiring needs
- Marketing and consulting skills missing from CV profile

❌ **5. Inefficient Skill Extraction**
- Regex word boundary matching is fragile
- Spacy EntityRuler with multi-token patterns is suboptimal
- Misses variations (e.g., "MLOps", "ML Ops", "Machine Learning Operations")
- No stemming/lemmatization

❌ **6. Cross-Encoder Inefficiency**
- Runs on individual jobs (not batched)
- Very slow for 500+ jobs
- Overkill modeling for simple task

❌ **7. Poor Ranking for Consulting Context**
- Your CV emphasizes **AI/ML/Data Science**, but:
  - Consulting roles often need **business acumen**, **client management**, **communication**
  - Your system has no cultural fit detection
  - Missing "Big 4" indicator, maturity detection

❌ **8. No Batch Scoring Output**
- Cannot return scores in batch (would need to process one-by-one)
- Difficult to scale for n8n workflows

❌ **9. Type Inconsistencies**
- Cross-encoder score normalization only applies within batch (unstable)
- Semantic scores not normalized across full dataset

❌ **10. Missing Consulting-Specific Logic**
- No detection of:
  - Strategy vs Implementation consulting
  - Firm size/prestige
  - Industry focus alignment
  - Client base (startups vs enterprises)

---

## 2. PROPOSED IMPROVEMENTS

### 2.1 Enhanced Scoring Strategy

#### New Three-Tier System:

**TIER 1: Fast Filtering (Eliminate noise)**
- Source validation (accept: Indeed, LinkedIn, GlassDoor, etc.)
- Language detection (French/English)
- Relevance classifier (binary: consulting-relevant or not)
- Minimum keyword presence

**TIER 2: Multi-Dimensional Scoring**

a) **Skill Matching Score** (25% weight)
- Improved extraction with fuzzy matching
- Skill categories: Core, Nice-to-Have, Industry-Specific
- Higher weight for core skills
- Variation detection (MLOps vs "Machine Learning Operations")

b) **Consulting Fit Score** (20% weight)
- Consulting keywords: "consulting", "confidentiality", "advisory", "strategy", "implementation"
- Firm prestige indicators: "McKinsey", "BCG", "Bain", "Deloitte", "EY", "Accenture"
- Project-based language detection
- Client-facing language indicators

c) **Seniority Match Score** (15% weight)
- Detect job level: Junior/Mid/Senior/Lead/Principal
- Match against CV profile (Senior AI/ML professionals)
- Penalize mismatch

d) **Semantic Relevance Score** (20% weight)
- Embeddings with better context (domain-specific models)
- Semantic categories for job functions

e) **Growth Potential Score** (10% weight)
- Emerging technologies (LLMs, AI Agents, etc.)
- High-growth industries
- Cutting-edge project indicators

f) **Cultural Alignment Score** (10% weight)
- Company size indication
- Remote/hybrid work preference
- Geographic preference

**TIER 3: Explainability Layer**
- Return matching skills with detection confidence
- Explain score breakdown
- Highlight match reasons
- Flag uncertainties

---

### 2.2 Consulting-Specific Enhancements

For **Olive Soft consulting targeting**, add:

```python
CONSULTING_KEYWORDS = {
    "strategy": 2.0,
    "transformation": 2.0,
    "advisory": 1.8,
    "implementation": 1.5,
    "consulting": 2.0,
    "client engagement": 1.5,
    "project delivery": 1.2,
    "stakeholder management": 1.3,
}

STRATEGIC_SKILLS = {
    "strategic thinking": 2.0,
    "business case development": 2.0,
    "solution architecture": 1.8,
    "change management": 1.5,
}

PRESTIGE_FIRMS = {
    "mckinsey": 2.0,
    "bcg": 2.0,
    "bain": 2.0,
    "deloitte": 1.5,
    "ey": 1.5,
    "accenture": 1.3,
    "sapient": 1.2,
}
```

---

### 2.3 Architecture Changes

| Component | Current | Proposed |
|-----------|---------|----------|
| **Skill Extraction** | Spacy EntityRuler | FuzzyWuzzy + lemmatization + n-gram matching |
| **Scoring Stages** | 3 stages | 6 dimensions, parallel computation |
| **API** | None | FastAPI with request/response schemas |
| **Response Format** | Raw DataFrames | Structured JSON with reasoning |
| **Seniority** | Not detected | Regex patterns + NLP classifier |
| **Consulting Logic** | Generic | Tailored with domain keywords |
| **Error Handling** | None | Comprehensive with fallbacks |
| **Scaling** | Single process | Async, batch-ready |
| **Monitoring** | None | Logging, metrics collection |

---

## 3. ISSUES WITH CURRENT PRODUCTION DEPLOYMENT

1. ❌ **No API** - Cannot be called by n8n directly
2. ❌ **Hardcoded CV** - Cannot update without code change
3. ❌ **No configuration** - Weights not adjustable
4. ❌ **Memory intensive** - Loads models in memory every run
5. ❌ **No error handling** - Crashes on malformed data
6. ❌ **No logging** - Cannot debug production issues
7. ❌ **N/A columns break pipeline** - Unhandled null values
8. ❌ **Inconsistent output** - Works only with full DataFrames

---

## 4. RECOMMENDED PRODUCTION STRATEGY

✅ **Separate concerns:**
- **API Layer** - FastAPI for HTTP interface
- **Scoring Pipeline** - Pure functions, testable
- **Feature Extraction** - Separate module
- **Model Management** - Singleton pattern for model loading
- **Configuration** - YAML/JSON for weights and thresholds
- **Logging & Monitoring** - Comprehensive tracing

✅ **Optimize for n8n:**
- Single job scoring endpoint (not batch)
- Structured JSON responses
- Error codes for fallbacks
- Response time < 5 seconds per job

✅ **Make it maintainable:**
- Dependency injection for models
- Unit tests
- Clear comments
- Modular design

---

## 5. NEXT STEPS

1. ✨ **Implement improved scoring logic** with all 6 dimensions
2. 🏗️ **Refactor architecture** into modules
3. 🔌 **Create FastAPI service** with proper schemas
4. 📊 **Add configuration system** for weights
5. 🧪 **Add comprehensive logging**
6. 📈 **Add metrics collection**
7. 🚀 **Package for deployment** (Docker optional)

---

**Status**: Ready for implementation
**Complexity**: Medium
**Time Estimate**: 4-6 hours for full implementation
**Dependencies**: FastAPI, pydantic, sentence-transformers, spacy, fuzzywuzzy

