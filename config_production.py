"""
Production Configuration for Olive Soft Job Scoring System
- Centralized configuration and skill/domain definitions
- Easy to update without code changes
"""

import json

# ============================================================================
# 1. OLIVE SOFT CV PROFILE - AI/ML/Data Science Focus
# ============================================================================

CV_SKILLS = {
    # Core Programming
    "python": 3,
    "sql": 3,
    "java": 2,
    "c++": 1,
    "typescript": 1,
    "javascript": 1,

    # Data & AI - PRIMARY FOCUS
    "machine learning": 3,
    "deep learning": 3,
    "nlp": 3,
    "data science": 3,
    "artificial intelligence": 3,
    "ai": 3,
    "data analysis": 2,
    "statistics": 2,
    "computer vision": 2,

    # Frameworks & Libraries
    "pandas": 3,
    "numpy": 2,
    "scikit-learn": 3,
    "tensorflow": 2,
    "pytorch": 2,
    "keras": 2,
    "matplotlib": 1,
    "seaborn": 1,

    # LLM & Advanced AI
    "transformers": 2,
    "hugging face": 2,
    "bert": 2,
    "gpt": 2,
    "llm": 2,
    "large language models": 2,
    "llama": 1,
    "mistral": 1,

    # Data Engineering
    "etl": 2,
    "data pipelines": 2,
    "airflow": 1,
    "spark": 1,
    "big data": 1,

    # Databases
    "postgresql": 2,
    "mysql": 2,
    "mongodb": 1,
    "redis": 1,

    # BI & Visualization
    "power bi": 2,
    "tableau": 1,
    "dashboarding": 1,

    # Cloud & DevOps
    "aws": 2,
    "azure": 1,
    "gcp": 1,
    "docker": 2,
    "kubernetes": 1,
    "git": 2,
    "linux": 2,
    "ci/cd": 1,

    # API & Backend
    "fastapi": 2,
    "flask": 2,
    "rest api": 2,
    "api design": 1,
}

# ============================================================================
# 2. CONSULTING-SPECIFIC ENHANCEMENTS
# ============================================================================

CONSULTING_KEYWORDS = {
    # Strategic/Advisory
    "consulting": 2.5,
    "consultant": 2.5,
    "advisory": 2.0,
    "strategy": 2.0,
    "transformation": 2.0,
    "strategic": 1.5,
    
    # Project/Implementation
    "implementation": 1.5,
    "project delivery": 1.3,
    "project management": 1.2,
    "delivery": 1.0,
    "execution": 1.0,
    
    # Client Engagement
    "client": 1.3,
    "stakeholder management": 1.3,
    "communication": 1.0,
    "collaboration": 1.0,
    "team leadership": 1.2,
    
    # Methodology
    "agile": 1.0,
    "scrum": 0.8,
    "waterfall": 0.5,
    "methodology": 1.0,
}

# Strategic skills valued in consulting
STRATEGIC_SKILLS = {
    "strategic thinking": 2.0,
    "business acumen": 1.8,
    "solution architecture": 1.8,
    "business case development": 1.5,
    "change management": 1.5,
    "problem solving": 1.2,
    "analytical thinking": 1.2,
}

# Prestigious consulting firms (reputation boost)
PRESTIGE_FIRMS = {
    "mckinsey": 2.5,
    "bcg": 2.5,
    "bain": 2.5,
    "boston": 2.5,
    "deloitte": 1.8,
    "ey": 1.8,
    "accenture": 1.5,
    "sapient": 1.3,
    "capgemini": 1.2,
    "ibm consulting": 1.2,
}

# ============================================================================
# 3. SENIORITY LEVELS
# ============================================================================

SENIORITY_KEYWORDS = {
    "senior": 3,
    "sr.": 3,
    "sr ": 3,
    "lead": 3,
    "principal": 4,
    "staff": 3,
    "architect": 2,
    "manager": 2,
    "director": 4,
    "vp": 4,
    "chief": 4,
    
    "mid-level": 2,
    "mid level": 2,
    "intermediate": 2,
    
    "junior": 1,
    "jr.": 1,
    "jr ": 1,
    "entry": 1,
    "graduate": 0,
    "intern": 0,
}

# ============================================================================
# 4. SCORING WEIGHTS - CONFIGURABLE
# ============================================================================

SCORING_WEIGHTS = {
    "skill_matching": 0.25,       # Exact skill matches
    "consulting_fit": 0.20,        # Consulting keywords + firm prestige
    "seniority_match": 0.15,       # Level alignment
    "semantic_relevance": 0.20,    # Embeddings-based
    "growth_potential": 0.10,      # Emerging tech + innovation
    "cultural_alignment": 0.10,    # Company/role characteristics
}

# Consulting vs Data Science weights - OPTIONAL OVERRIDE
CONSULTING_WEIGHTS = {
    "skill_matching": 0.20,
    "consulting_fit": 0.35,         # Higher weight for consulting fit
    "seniority_match": 0.15,
    "semantic_relevance": 0.15,
    "growth_potential": 0.10,
    "cultural_alignment": 0.05,
}

# ============================================================================
# 5. SENIORITY TARGETING
# ============================================================================

TARGET_SENIORITY = "senior"  # Target: Senior or above
SENIORITY_LEVELS = {
    0: "internship",
    1: "junior",
    2: "mid-level",
    3: "senior",
    4: "leadership"
}

# ============================================================================
# 6. FILTERING THRESHOLDS
# ============================================================================

FILTERS = {
    "min_score": 0.50,                 # Minimum final score to include
    "min_skill_score": 0.10,           # Minimum skill match (low bar)
    "min_semantic_score": 0.30,        # Minimum semantic relevance
    
    # Source acceptance
    "accepted_sources": [
        "indeed",
        "linkedin", 
        "glassdoor",
        "ziprecruiters",
        "workable",
        "hired",
        "removebg"
    ],
    
    # Content requirements
    "min_description_length": 100,     # Minimum job description size
    "languages": ["en", "fr"],         # Accepted languages
}

# ============================================================================
# 7. MODEL CONFIGURATION
# ============================================================================

MODEL_CONFIG = {
    "bi_encoder": "sentence-transformers/all-MiniLM-L6-v2",
    "cross_encoder": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "language": "fr_core_news_sm",  # French NLP model
    "device": "cpu",  # Use "cuda" if GPU available
    "batch_size": 32,
}

# ============================================================================
# 8. EMERGING TECHNOLOGIES (Growth potential)
# ============================================================================

EMERGING_TECH = {
    "llm": 2.0,
    "large language model": 2.0,
    "gpt": 1.8,
    "gpt-4": 2.0,
    "chatgpt": 1.5,
    "generative ai": 2.0,
    "ai agent": 2.0,
    "agent": 1.2,
    "retrieval augmented generation": 2.0,
    "rag": 2.0,
    "prompt engineering": 1.8,
    "fine-tuning": 1.5,
    "vector database": 1.5,
    "embedding": 1.2,
}

# ============================================================================
# 9. INDUSTRY FOCUS (Optional - for future enhancement)
# ============================================================================

INDUSTRIES = {
    "technology": 2.0,
    "fintech": 1.8,
    "software": 2.0,
    "saas": 1.8,
    "healthcare": 1.2,
    "finance": 1.5,
    "consulting": 2.0,
}

# ============================================================================
# 10. OUTPUT REASONS TEMPLATES
# ============================================================================

REASON_TEMPLATES = {
    "high_skill_match": "Strong match with {} required skills",
    "consulting_fit": "Clear consulting opportunity ({})",
    "seniority_match": "Perfect seniority alignment ({})",
    "semantic_match": "Relevant work in {} domain",
    "emerging_tech": "Opportunity in emerging field: {}",
    "prestige_firm": "Opportunity with prestigious firm: {}",
}
