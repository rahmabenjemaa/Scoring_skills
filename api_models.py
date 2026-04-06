"""
API Request/Response Schemas using Pydantic
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class JobScoringRequest(BaseModel):
    """Request body for single job scoring."""
    
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Job description")
    company: Optional[str] = Field(None, description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    source: Optional[str] = Field(None, description="Job source (LinkedIn, Indeed, etc)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior ML Engineer",
                "description": "We're looking for a Senior ML Engineer with 5+ years experience in NLP and transformers. You will work on our core LLM platform...",
                "company": "TechCorp AI",
                "location": "Paris",
                "source": "LinkedIn"
            }
        }


class BatchScoringRequest(BaseModel):
    """Request body for batch job scoring."""
    
    jobs: List[JobScoringRequest] = Field(..., description="List of jobs to score")
    use_consulting_mode: Optional[bool] = Field(False, description="Use consulting-focused scoring")
    
    class Config:
        json_schema_extra = {
            "example": {
                "jobs": [
                    {
                        "title": "Senior ML Engineer",
                        "description": "...",
                        "company": "TechCorp",
                        "location": "Paris"
                    }
                ],
                "use_consulting_mode": False
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class DimensionScores(BaseModel):
    """Breakdown of 6-dimensional scores."""
    
    skill_matching: float = Field(..., ge=0, le=1, description="CV skill match score")
    consulting_fit: float = Field(..., ge=0, le=1, description="Consulting opportunity score")
    seniority_match: float = Field(..., ge=0, le=1, description="Seniority alignment score")
    semantic_relevance: float = Field(..., ge=0, le=1, description="Semantic similarity score")
    growth_potential: float = Field(..., ge=0, le=1, description="Emerging tech score")
    cultural_alignment: float = Field(..., ge=0, le=1, description="Work culture fit score")


class SeniorityInfo(BaseModel):
    """Detected seniority information."""
    
    level: int = Field(..., ge=0, le=4, description="Seniority level (0-4)")
    name: str = Field(..., description="Seniority level name")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")


class SkillsInfo(BaseModel):
    """Extracted skills and frequency."""
    
    extracted: Dict[str, int] = Field(..., description="Skill -> frequency map")
    weight_score: float = Field(..., ge=0, le=1, description="Weighted skills score")
    count: int = Field(..., ge=0, description="Number of skills matched")


class ConsultingInfo(BaseModel):
    """Consulting opportunity indicators."""
    
    fit_score: float = Field(..., ge=0, le=1, description="Consulting fit score")
    keywords: List[str] = Field(..., description="Detected consulting keywords")
    prestige_firm: Optional[str] = Field(None, description="Prestige firm detected")
    strategic_skills: List[str] = Field(..., description="Strategic skills found")


class EmergingTechInfo(BaseModel):
    """Emerging technology indicators."""
    
    score: float = Field(..., ge=0, le=1, description="Emerging tech score")
    technologies: List[str] = Field(..., description="Detected emerging technologies")


class WorkModeInfo(BaseModel):
    """Work mode and flexibility."""
    
    is_remote: Optional[bool] = Field(None, description="Is remote/hybrid")
    mode: str = Field(..., description="Work mode (fully_remote, hybrid, on_site, unknown)")


class FeaturesExtraction(BaseModel):
    """Complete feature extraction breakdown."""
    
    skills: SkillsInfo
    seniority: SeniorityInfo
    consulting: ConsultingInfo
    emerging_tech: EmergingTechInfo
    work_mode: WorkModeInfo


class JobScoringResponse(BaseModel):
    """Successful scoring response."""
    
    success: bool = Field(True, description="Scoring succeeded")
    final_score: float = Field(..., ge=0, le=1, description="Final score 0-1")
    match_percentage: float = Field(..., ge=0, le=1, description="Match as percentage")
    
    # Dimension breakdown
    dimensions: DimensionScores = Field(..., description="6-dimensional score breakdown")
    
    # Features
    features: FeaturesExtraction = Field(..., description="Extracted features")
    
    # Reasoning
    reasons: List[str] = Field(..., description="Match reasons (human-readable)")
    top_reason: str = Field(..., description="Primary match reason")
    
    # Quick reference
    skills_detected: List[str] = Field(..., description="Matched CV skills")
    seniority: str = Field(..., description="Detected seniority level")
    is_consulting_opportunity: bool = Field(..., description="Is consulting role")
    prestige_firm: Optional[str] = Field(None, description="Prestige firm if detected")
    emerging_technologies: List[str] = Field(..., description="Detected emerging tech")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
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
                    "Perfect seniority match (Senior)"
                ],
                "top_reason": "Strong skill match: Python, NLP, transformers",
                "seniority": "senior",
                "is_consulting_opportunity": False,
                "emerging_technologies": ["llm", "gpt"]
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    
    success: bool = Field(False, description="Operation failed")
    error: str = Field(..., description="Error message")
    final_score: float = Field(0, description="Score (0 on error)")
    match_percentage: float = Field(0.0, description="Match percentage (0 on error)")


class BatchScoringResponse(BaseModel):
    """Batch scoring response."""
    
    success: bool = Field(..., description="All jobs scored successfully")
    total_jobs: int = Field(..., description="Total jobs scored")
    successful_scores: int = Field(..., description="Successfully scored count")
    failed_scores: int = Field(..., description="Failed score count")
    results: List[Dict[str, Any]] = Field(..., description="Individual scoring results")
    average_score: float = Field(..., ge=0, le=1, description="Average score across successful jobs")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    
    status: str = Field("healthy", description="Service status")
    version: str = Field(..., description="API version")
    models_loaded: bool = Field(..., description="All models loaded")
    timestamp: str = Field(..., description="Response timestamp")


class ScoringConfig(BaseModel):
    """Current scoring configuration."""
    
    weights: Dict[str, float] = Field(..., description="Scoring dimension weights")
    target_seniority: str = Field(..., description="Target seniority level")
    minimum_score_threshold: float = Field(..., description="Minimum acceptable score")
