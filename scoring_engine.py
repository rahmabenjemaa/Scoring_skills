"""
Scoring Engine - Production Version
6-dimensional scoring: Skills, Consulting Fit, Seniority, Semantic, Growth, Culture
"""

import logging
from typing import Dict, Optional, Tuple, List
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from feature_extractor import UnifiedFeatureExtractor
from config_production import (
    CV_SKILLS,
    SCORING_WEIGHTS,
    CONSULTING_WEIGHTS,
    MODEL_CONFIG,
    TARGET_SENIORITY,
)

logger = logging.getLogger(__name__)


class ScoringEngine:
    """
    Production-grade scoring engine with 6 dimensions.
    
    Dimensions:
    1. Skill Matching (25%) - Exact CV skill matches
    2. Consulting Fit (20%) - Consulting keywords, prestige firms
    3. Seniority Match (15%) - Job level alignment
    4. Semantic Relevance (20%) - Embeddings-based
    5. Growth Potential (10%) - Emerging tech
    6. Cultural Alignment (10%) - Work mode, company size
    """
    
    def __init__(self, cv_skills: Dict[str, int] = None, weights: Dict = None):
        """Initialize scoring engine with models and extractors."""
        if cv_skills is None:
            cv_skills = CV_SKILLS
        
        self.cv_skills = cv_skills
        self.weights = weights or SCORING_WEIGHTS
        
        # Initialize feature extraction
        self.feature_extractor = UnifiedFeatureExtractor(cv_skills)
        
        # Initialize semantic models
        logger.info("🔹 Loading semantic models...")
        self.bi_encoder = SentenceTransformer(MODEL_CONFIG["bi_encoder"])
        
        # Prepare CV embedding
        cv_text = " ".join(cv_skills.keys())
        self.cv_embedding = self.bi_encoder.encode(cv_text, convert_to_tensor=True)
        self.cv_text = cv_text
        
        logger.info("✅ Scoring engine initialized")
    
    # ==========================================================================
    # DIMENSION 1: Skill Matching Score
    # ==========================================================================
    
    def compute_skill_score(self, features: Dict) -> float:
        """
        Score based on CV skill matches.
        
        Returns: 0-1
        """
        skill_weight = features["skills"]["weight_score"]
        skill_count = features["skills"]["count"]
        
        # Bonus for multiple skill matches
        if skill_count == 0:
            return 0.0
        
        diversity_bonus = min(skill_count / 10, 0.2)  # +20% max for diverse skills
        
        return min(skill_weight + diversity_bonus, 1.0)
    
    # ==========================================================================
    # DIMENSION 2: Consulting Fit Score
    # ==========================================================================
    
    def compute_consulting_fit_score(self, features: Dict) -> float:
        """
        Score consulting opportunity indicators.
        
        Returns: 0-1
        """
        consulting_score = features["consulting"]["fit_score"]
        has_prestige_firm = features["consulting"]["prestige_firm"] is not None
        
        # Significant boost for prestigious firms
        prestige_boost = 0.3 if has_prestige_firm else 0
        
        return min(consulting_score + prestige_boost, 1.0)
    
    # ==========================================================================
    # DIMENSION 3: Seniority Match Score
    # ==========================================================================
    
    def compute_seniority_match_score(self, features: Dict) -> float:
        """
        Score seniority alignment with target (Senior).
        
        Returns: 0-1
        """
        detected_level = features["seniority"]["level"]
        target_level = 3  # Senior
        
        # Use the detector's match score
        level_diff = abs(detected_level - target_level)
        
        if level_diff == 0:
            return 1.0
        elif level_diff == 1:
            return 0.7
        elif level_diff == 2:
            return 0.4
        else:
            return 0.1
    
    # ==========================================================================
    # DIMENSION 4: Semantic Relevance Score
    # ==========================================================================
    
    def compute_semantic_score(self, text: str) -> float:
        """
        Score semantic similarity using embeddings.
        
        Returns: 0-1 (cosine similarity)
        """
        try:
            job_embedding = self.bi_encoder.encode(text, convert_to_tensor=True)
            
            cosine_score = cosine_similarity(
                self.cv_embedding.cpu().reshape(1, -1),
                job_embedding.cpu().reshape(1, -1)
            )[0][0]
            
            return float(cosine_score)
        except Exception as e:
            logger.warning(f"Semantic scoring failed: {e}")
            return 0.0
    
    # ==========================================================================
    # DIMENSION 5: Growth Potential Score
    # ==========================================================================
    
    def compute_growth_potential_score(self, features: Dict) -> float:
        """
        Score opportunity in emerging/growth areas.
        
        Returns: 0-1
        """
        emerging_score = features["emerging_tech"]["score"]
        emerging_count = len(features["emerging_tech"]["technologies"])
        
        # Bonus for multiple emerging tech mentions
        diversity_bonus = min(emerging_count * 0.1, 0.2)
        
        return min(emerging_score + diversity_bonus, 1.0)
    
    # ==========================================================================
    # DIMENSION 6: Cultural Alignment Score
    # ==========================================================================
    
    def compute_cultural_alignment_score(self, features: Dict) -> float:
        """
        Score work mode and company culture fit.
        
        Returns: 0-1
        """
        # Work mode preference: Prefer hybrid/remote
        work_mode = features["work_mode"]["mode"]
        
        if work_mode == "fully_remote":
            return 0.9
        elif work_mode == "hybrid":
            return 0.8
        elif work_mode == "on_site":
            return 0.6
        else:
            return 0.5  # Unknown = neutral
    
    # ==========================================================================
    # COMPREHENSIVE SCORING
    # ==========================================================================
    
    def score_job(self, title: str, description: str) -> Dict:
        """
        Score a single job across all 6 dimensions.
        
        Returns comprehensive scoring breakdown with reasoning.
        """
        try:
            # Validate input
            if not description or len(str(description).strip()) < 50:
                return self._create_error_response("Description too short")
            
            # Extract all features
            logger.debug(f"Extracting features for: {title}")
            features = self.feature_extractor.extract_all(description, title)
            
            # Compute 6 scores
            skill_score = self.compute_skill_score(features)
            consulting_score = self.compute_consulting_fit_score(features)
            seniority_score = self.compute_seniority_match_score(features)
            semantic_score = self.compute_semantic_score(description)
            growth_score = self.compute_growth_potential_score(features)
            cultural_score = self.compute_cultural_alignment_score(features)
            
            # Aggregate final score
            final_score = (
                self.weights["skill_matching"] * skill_score +
                self.weights["consulting_fit"] * consulting_score +
                self.weights["seniority_match"] * seniority_score +
                self.weights["semantic_relevance"] * semantic_score +
                self.weights["growth_potential"] * growth_score +
                self.weights["cultural_alignment"] * cultural_score
            )
            
            # Generate reasoning
            reasons = self._generate_reasons(
                skill_score, consulting_score, seniority_score,
                semantic_score, growth_score, cultural_score,
                features
            )
            
            return {
                # Final result
                "success": True,
                "final_score": round(final_score, 3),
                "match_percentage": round(final_score, 2),
                
                # Dimension scores
                "dimensions": {
                    "skill_matching": round(skill_score, 3),
                    "consulting_fit": round(consulting_score, 3),
                    "seniority_match": round(seniority_score, 3),
                    "semantic_relevance": round(semantic_score, 3),
                    "growth_potential": round(growth_score, 3),
                    "cultural_alignment": round(cultural_score, 3),
                },
                
                # Detailed features
                "features": features,
                
                # Reasoning
                "reasons": reasons,
                "top_reason": reasons[0] if reasons else "Moderate match",
                
                # Skills detected
                "skills_detected": list(features["skills"]["extracted"].keys()),
                "seniority": features["seniority"]["name"],
                
                # Consulting indicators
                "is_consulting_opportunity": consulting_score > 0.5,
                "prestige_firm": features["consulting"]["prestige_firm"],
                
                # Emerging tech
                "emerging_technologies": features["emerging_tech"]["technologies"],
            }
        
        except Exception as e:
            logger.error(f"Error scoring job: {e}")
            return self._create_error_response(f"Scoring error: {str(e)}")
    
    def _generate_reasons(self, skill: float, consulting: float, seniority: float,
                        semantic: float, growth: float, cultural: float,
                        features: Dict) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []
        
        # Skill-based reasons
        if skill > 0.7:
            skills_list = ", ".join(list(features["skills"]["extracted"].keys())[:3])
            reasons.append(f"Strong skill match: {skills_list}")
        elif skill > 0.4:
            reasons.append("Good skill match")
        
        # Consulting-based reasons
        if consulting > 0.7:
            if features["consulting"]["prestige_firm"]:
                reasons.append(f"Prestigious consulting opportunity at {features['consulting']['prestige_firm']}")
            else:
                reasons.append("Clear consulting opportunity")
        
        # Seniority reasons
        if seniority > 0.8:
            reasons.append(f"Perfect seniority match ({features['seniority']['name']})")
        elif seniority > 0.6:
            reasons.append(f"Good seniority alignment ({features['seniority']['name']})")
        
        # Semantic reasons
        if semantic > 0.7:
            reasons.append("Highly relevant role content")
        
        # Growth/Innovation reasons
        if growth > 0.5 and features["emerging_tech"]["technologies"]:
            tech_list = ", ".join(features["emerging_tech"]["technologies"][:2])
            reasons.append(f"Cutting-edge opportunity: {tech_list}")
        
        # Work mode reasons
        if features["work_mode"]["mode"] in ["fully_remote", "hybrid"]:
            reasons.append(f"Work mode: {features['work_mode']['mode']}")
        
        return reasons if reasons else ["Moderate overall match"]
    
    def _create_error_response(self, error_msg: str) -> Dict:
        """Create standard error response."""
        return {
            "success": False,
            "error": error_msg,
            "final_score": 0,
            "match_percentage": 0.0,
        }
    
    # ==========================================================================
    # BATCH PROCESSING
    # ==========================================================================
    
    def score_batch(self, jobs: List[Dict]) -> List[Dict]:
        """
        Score multiple jobs.
        
        Args:
            jobs: List of dicts with 'title' and 'description'
        
        Returns:
            List of scoring results
        """
        results = []
        for i, job in enumerate(jobs):
            logger.info(f"Scoring job {i+1}/{len(jobs)}: {job.get('title', 'Unknown')}")
            result = self.score_job(
                job.get("title", ""),
                job.get("description", "")
            )
            results.append(result)
        
        return results


# ============================================================================
# Specialized Scoring Engine for Consulting Context (Optional)
# ============================================================================

class ConsultingFocusedScoringEngine(ScoringEngine):
    """
    Specialized scoring engine with higher weight for consulting indicators.
    Use when targeting consulting opportunities specifically.
    """
    
    def __init__(self, cv_skills: Dict[str, int] = None):
        super().__init__(cv_skills, weights=CONSULTING_WEIGHTS)
        logger.info("Consulting-focused scoring engine initialized")
