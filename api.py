"""
FastAPI Application - Production Job Scoring API
Exposing the scoring engine as an HTTP service for n8n integration
"""

import logging
from datetime import datetime
from typing import Optional, Union
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn

from scoring_engine import ScoringEngine, ConsultingFocusedScoringEngine
from api_models import (
    JobScoringRequest,
    BatchScoringRequest,
    JobScoringResponse,
    ErrorResponse,
    BatchScoringResponse,
    HealthCheckResponse,
    ScoringConfig,
)
from config_production import SCORING_WEIGHTS, CONSULTING_WEIGHTS, TARGET_SENIORITY

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL STATE (Models)
# ============================================================================

scoring_engine = None
consulting_scoring_engine = None

# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    - Load models on startup (in thread pool to avoid blocking event loop)
    - Clean up on shutdown
    """
    # Startup
    global scoring_engine, consulting_scoring_engine
    
    logger.info("🚀 Starting Olive Soft Job Scoring API...")
    try:
        # Load models in thread pool to avoid blocking async event loop
        def _load_engines():
            logger.info("📦 Loading ScoringEngine...")
            engine = ScoringEngine()
            logger.info("✅ ScoringEngine loaded")
            
            logger.info("📦 Loading ConsultingFocusedScoringEngine...")
            consulting_engine = ConsultingFocusedScoringEngine()
            logger.info("✅ ConsultingFocusedScoringEngine loaded")
            
            return engine, consulting_engine
        
        # Load with timeout to prevent hanging
        loop = asyncio.get_event_loop()
        scoring_engine, consulting_scoring_engine = await asyncio.wait_for(
            asyncio.to_thread(_load_engines),
            timeout=120  # 2 minute timeout for model loading
        )
        logger.info("✅ All models loaded successfully - API ready!")
    except asyncio.TimeoutError:
        logger.error("❌ Model loading timed out after 120 seconds")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to load models: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API...")
    logger.info("✅ Cleanup complete")

# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Olive Soft Job Scoring API",
    description="Production-grade semantic job scoring for opportunity detection",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for n8n integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for n8n flexibility
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log validation errors for debugging."""
    logger.error(f"❌ Validation error: {exc.errors()}")
    logger.error(f"Request body type: {type(exc.body)}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc.body)[:200],  # First 200 chars for debugging
        },
    )

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _get_engine(use_consulting: bool = False):
    """Get appropriate scoring engine."""
    if use_consulting:
        if consulting_scoring_engine is None:
            raise RuntimeError("Consulting engine not initialized")
        return consulting_scoring_engine
    else:
        if scoring_engine is None:
            raise RuntimeError("Scoring engine not initialized")
        return scoring_engine

# ============================================================================
# ENDPOINTS
# ============================================================================

# ─────────────────────────────────────────────────────────────────────────
# 1. HEALTH CHECK
# ─────────────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    tags=["System"]
)
async def health_check():
    """Check if API and models are ready."""
    models_loaded = scoring_engine is not None and consulting_scoring_engine is not None
    
    return HealthCheckResponse(
        status="healthy" if models_loaded else "degraded",
        version="1.0.0",
        models_loaded=models_loaded,
        timestamp=datetime.now().isoformat(),
    )

# ─────────────────────────────────────────────────────────────────────────
# DEBUG: Echo request body (for n8n troubleshooting)
# ─────────────────────────────────────────────────────────────────────────

@app.post(
    "/debug/echo",
    summary="Echo request for debugging",
    tags=["Debug"]
)
async def debug_echo(request: Request):
    """Receive any JSON and echo it back (for debugging n8n payloads)."""
    try:
        body = await request.json()
        logger.info(f"📨 Received body: {body}")
        return {
            "received": body,
            "type": str(type(body)),
            "keys": list(body.keys()) if isinstance(body, dict) else "not a dict"
        }
    except Exception as e:
        logger.error(f"❌ Debug echo error: {e}")
        return {"error": str(e)}

# ─────────────────────────────────────────────────────────────────────────
# 2. SINGLE JOB SCORING
# ─────────────────────────────────────────────────────────────────────────

@app.post(
    "/score",
    response_model=Union[JobScoringResponse, ErrorResponse],
    summary="Score a single job",
    tags=["Scoring"],
    responses={
        200: {"description": "Scoring successful"},
        400: {"description": "Invalid request"},
        500: {"description": "Scoring error"},
    }
)
async def score_job(
    request: JobScoringRequest,
    consulting_mode: Optional[bool] = False
):
    """
    Score a single job opportunity.
    
    **Parameters:**
    - `title`: Job title
    - `description`: Job description (must be at least 50 chars)
    - `company`: Company name (optional)
    - `location`: Job location (optional)
    - `source`: Job source like 'LinkedIn', 'Indeed' (optional)
    - `consulting_mode`: Use consulting-focused scoring (optional)
    
    **Returns:**
    - `final_score`: Score 0-1
    - `dimensions`: Breakdown of 6 scoring dimensions
    - `reasons`: Human-readable match reasons
    - `features`: Extracted features (skills, seniority, etc)
    
    **Example:**
    ```json
    {
        "title": "Senior ML Engineer",
        "description": "Looking for an experienced ML engineer with NLP expertise...",
        "company": "TechCorp",
        "location": "Paris"
    }
    ```
    """
    try:
        logger.info(f"📊 Scoring job: {request.title}")
        
        # Get appropriate engine
        engine = _get_engine(consulting_mode)
        
        # Score the job
        result = engine.score_job(request.title, request.description)
        
        if not result.get("success", False):
            return ErrorResponse(
                error=result.get("error", "Unknown error"),
                success=False
            )
        
        # Convert to response model
        return JobScoringResponse(**result)
    
    except Exception as e:
        logger.error(f"❌ Error scoring job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scoring failed: {str(e)}"
        )

# ─────────────────────────────────────────────────────────────────────────
# 3. BATCH JOB SCORING
# ─────────────────────────────────────────────────────────────────────────

@app.post(
    "/score/batch",
    response_model=BatchScoringResponse,
    summary="Score multiple jobs",
    tags=["Scoring"],
)
async def score_batch(request: BatchScoringRequest):
    """
    Score multiple jobs in a single request.
    
    **Best for:**
    - Processing multiple jobs from a CSV export
    - Batch operations in n8n workflows
    - Comparing multiple job offers
    
    **Note:** Each job is scored independently. This endpoint is 
    recommended for 2-20 jobs. For larger batches, implement client-side 
    parallelization (score jobs individually in parallel requests).
    """
    try:
        logger.info(f"📊 Batch scoring {len(request.jobs)} jobs")
        
        # Get appropriate engine
        engine = _get_engine(request.use_consulting_mode)
        
        # Prepare jobs
        jobs = [job.dict() for job in request.jobs]
        
        # Score all jobs
        results = engine.score_batch(jobs)
        
        # Compute statistics
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful
        
        avg_score = 0
        if successful > 0:
            scores = [r["final_score"] for r in results if r.get("success", False)]
            avg_score = sum(scores) / len(scores)
        
        return BatchScoringResponse(
            success=failed == 0,
            total_jobs=len(results),
            successful_scores=successful,
            failed_scores=failed,
            results=results,
            average_score=round(avg_score, 3),
        )
    
    except Exception as e:
        logger.error(f"❌ Error in batch scoring: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch scoring failed: {str(e)}"
        )

# ─────────────────────────────────────────────────────────────────────────
# 4. CONFIGURATION ENDPOINT
# ─────────────────────────────────────────────────────────────────────────

@app.get(
    "/config",
    response_model=ScoringConfig,
    summary="Get current scoring configuration",
    tags=["System"]
)
async def get_config():
    """
    Get the current scoring configuration 
    (weights, thresholds, target seniority).
    """
    return ScoringConfig(
        weights=SCORING_WEIGHTS,
        target_seniority=TARGET_SENIORITY,
        minimum_score_threshold=0.5,
    )

# ─────────────────────────────────────────────────────────────────────────
# 5. CONSULTING MODE ENDPOINT
# ─────────────────────────────────────────────────────────────────────────

@app.get(
    "/config/consulting",
    response_model=ScoringConfig,
    summary="Get consulting-focused scoring configuration",
    tags=["System"]
)
async def get_consulting_config():
    """
    Get the consulting-focused scoring configuration 
    (higher weight on consulting indicators).
    """
    return ScoringConfig(
        weights=CONSULTING_WEIGHTS,
        target_seniority=TARGET_SENIORITY,
        minimum_score_threshold=0.5,
    )

# ─────────────────────────────────────────────────────────────────────────
# 6. DEMO ENDPOINT
# ─────────────────────────────────────────────────────────────────────────

@app.post(
    "/demo",
    response_model=JobScoringResponse,
    summary="Demo scoring with example job",
    tags=["Demo"]
)
async def demo_score():
    """
    Demo endpoint - score a sample job to test the API.
    
    Useful for:
    - Testing API connectivity
    - Understanding response format
    - Verifying model loading
    """
    example_job = JobScoringRequest(
        title="Senior AI/ML Consultant at McKinsey",
        description="""
        McKinsey is seeking a Senior AI/ML Consultant to join our AI & Analytics practice.
        
        Responsibilities:
        - Lead AI/ML consulting engagements for Fortune 500 clients
        - Design machine learning solutions for strategic business challenges
        - Work with Python, TensorFlow, and PyTorch for model development
        - Mentor junior consultants on NLP and deep learning techniques
        - Develop transformation strategies using generative AI and LLMs
        
        Requirements:
        - 5+ years experience in machine learning and data science
        - Strong proficiency in Python, SQL, and cloud platforms (AWS, Azure)
        - Experience with transformers, BERT, GPT models
        - Excellent consulting and communication skills
        - Strategic business thinking
        - Experience with data pipelines and ETL processes
        """,
        company="McKinsey & Company",
        location="Paris, France",
        source="LinkedIn"
    )
    
    return await score_job(example_job, consulting_mode=True)

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API root endpoint with documentation link."""
    return {
        "message": "Olive Soft Job Scoring API",
        "version": "1.0.0",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "GET /health",
            "score_single": "POST /score",
            "score_batch": "POST /score/batch",
            "configuration": "GET /config",
            "demo": "POST /demo",
        },
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.detail}")
    return {
        "success": False,
        "error": exc.detail,
        "final_score": 0,
        "match_percentage": 0.0,
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
