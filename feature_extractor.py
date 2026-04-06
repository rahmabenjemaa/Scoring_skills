"""
Feature Extractor Module - Production Version
Routes: Skill extraction, seniority detection, content classification
"""

import re
from typing import Dict, List, Tuple, Optional
from fuzzywuzzy import fuzz
import spacy
from config_production import (
    CV_SKILLS,
    SENIORITY_KEYWORDS,
    CONSULTING_KEYWORDS,
    STRATEGIC_SKILLS,
    EMERGING_TECH,
    PRESTIGE_FIRMS,
)


class SkillExtractor:
    """
    Advanced skill extraction with:
    - Fuzzy matching for variations
    - Multi-token recognition
    - Frequency scoring
    """
    
    def __init__(self, skills_dict: Dict[str, int]):
        self.skills_dict = skills_dict
        self.skill_names = list(skills_dict.keys())
        
        # Initialize NLP pipeline
        try:
            self.nlp = spacy.load("fr_core_news_sm")
        except OSError:
            print("⚠️  French NLP model not found. Using basic processing.")
            self.nlp = None
    
    def extract(self, text: str, threshold: int = 80) -> Dict[str, int]:
        """
        Extract skills with fuzzy matching.
        
        Args:
            text: Job description text (lowercase)
            threshold: Fuzzy match confidence (0-100)
        
        Returns:
            Dict mapping skill -> frequency count
        """
        text_lower = text.lower()
        extracted = {}
        
        for skill in self.skill_names:
            # Exact match first (fastest)
            if skill in text_lower:
                count = text_lower.count(skill)
                extracted[skill] = extracted.get(skill, 0) + count
            
            # Fuzzy match for variations
            else:
                # Check for partial matches (skill variations)
                if self._fuzzy_match(skill, text_lower, threshold):
                    extracted[skill] = extracted.get(skill, 0) + 1
        
        return extracted
    
    def _fuzzy_match(self, skill: str, text: str, threshold: int = 80) -> bool:
        """Check if skill appears with fuzzy matching."""
        # Split text into tokens for comparison
        tokens = text.split()
        for token in tokens:
            if fuzz.partial_ratio(skill, token) >= threshold:
                return True
        return False
    
    def get_skill_weights(self, extracted_skills: Dict[str, int]) -> float:
        """
        Compute weighted skill score.
        
        Returns: Normalized score 0-1
        """
        if not self.skills_dict:
            return 0.0
        
        total_weight = sum(self.skills_dict.values())
        matched_weight = 0
        
        for skill, frequency in extracted_skills.items():
            weight = self.skills_dict.get(skill, 0)
            matched_weight += weight * min(frequency, 2)  # Cap frequency at 2
        
        return min(matched_weight / total_weight, 1.0)


class SeniorityDetector:
    """Detect job seniority level from text."""
    
    def __init__(self):
        self.seniority_keywords = SENIORITY_KEYWORDS
    
    def detect(self, text: str) -> Tuple[int, str, float]:
        """
        Detect seniority level from job text.
        
        Returns:
            (level: 0-4, description: str, confidence: 0-1)
        """
        text_lower = text.lower()
        
        # Search for seniority indicators (priority order)
        found_keywords = {}
        
        for keyword, level in self.seniority_keywords.items():
            if keyword in text_lower:
                # Word boundary check to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    found_keywords[keyword] = level
        
        if not found_keywords:
            return 2, "mid-level", 0.3  # Default to mid-level with low confidence
        
        # Get highest seniority level found
        max_level = max(found_keywords.values())
        confidence = min(len(found_keywords) * 0.2, 0.9)  # More mentions = higher confidence
        
        level_name = {
            0: "internship",
            1: "junior",
            2: "mid-level",
            3: "senior",
            4: "leadership"
        }.get(max_level, "unknown")
        
        return max_level, level_name, confidence
    
    def seniority_match_score(self, detected_level: int, target_level: int = 3) -> float:
        """
        Score how well detected level matches target.
        
        Returns: 1.0 if match, 0.0 if very different
        """
        level_diff = abs(detected_level - target_level)
        
        if level_diff == 0:
            return 1.0
        elif level_diff == 1:
            return 0.7
        elif level_diff == 2:
            return 0.4
        else:
            return 0.1


class ConsultingFitDetector:
    """Detect consulting opportunity indicators."""
    
    def __init__(self):
        self.consulting_keywords = CONSULTING_KEYWORDS
        self.prestige_firms = PRESTIGE_FIRMS
        self.strategic_skills = STRATEGIC_SKILLS
    
    def detect_consulting_keywords(self, text: str) -> Tuple[float, List[str]]:
        """
        Detect consulting-related keywords.
        
        Returns:
            (score: 0-1, found_keywords: list)
        """
        text_lower = text.lower()
        found = []
        total_weight = 0
        max_weight = sum(self.consulting_keywords.values())
        
        for keyword, weight in self.consulting_keywords.items():
            if keyword in text_lower:
                found.append(keyword)
                total_weight += weight
        
        score = min(total_weight / max_weight, 1.0) if max_weight > 0 else 0
        
        return score, found
    
    def detect_prestige_firm(self, text: str) -> Tuple[float, Optional[str]]:
        """
        Detect if job is from a prestigious consulting firm.
        
        Returns:
            (boost: 0-1, firm_name: str)
        """
        text_lower = text.lower()
        
        for firm, weight in self.prestige_firms.items():
            if firm in text_lower:
                boost = min(weight / 2.5, 1.0)  # Normalize to 0-1
                return boost, firm
        
        return 0, None
    
    def detect_strategic_focus(self, text: str) -> Tuple[float, List[str]]:
        """
        Detect strategic/advisory focus.
        
        Returns:
            (score: 0-1, found_skills: list)
        """
        text_lower = text.lower()
        found = []
        total_weight = 0
        max_weight = sum(self.strategic_skills.values())
        
        for skill, weight in self.strategic_skills.items():
            if skill in text_lower:
                found.append(skill)
                total_weight += weight
        
        score = min(total_weight / max_weight, 1.0) if max_weight > 0 else 0
        
        return score, found
    
    def compute_consulting_fit_score(self, text: str) -> Tuple[float, Dict]:
        """
        Comprehensive consulting fit score.
        
        Returns:
            (score: 0-1, breakdown: dict)
        """
        keywords_score, keywords = self.detect_consulting_keywords(text)
        prestige_score, prestige_firm = self.detect_prestige_firm(text)
        strategic_score, strategic = self.detect_strategic_focus(text)
        
        # Combine: base consulting keywords + prestige + strategic focus
        combined = (
            0.5 * keywords_score +
            0.3 * prestige_score +
            0.2 * strategic_score
        )
        
        return min(combined, 1.0), {
            "keywords": keywords,
            "prestige_firm": prestige_firm,
            "strategic_skills": strategic,
        }


class EmergingTechDetector:
    """Detect emerging/cutting-edge technologies."""
    
    def __init__(self):
        self.emerging_tech = EMERGING_TECH
    
    def detect(self, text: str) -> Tuple[float, List[str]]:
        """
        Detect emerging tech mentions.
        
        Returns:
            (score: 0-1, technologies: list)
        """
        text_lower = text.lower()
        found = []
        total_weight = 0
        max_weight = sum(self.emerging_tech.values())
        
        for tech, weight in self.emerging_tech.items():
            if tech in text_lower:
                found.append(tech)
                total_weight += weight
        
        score = min(total_weight / max_weight, 1.0) if max_weight > 0 else 0
        
        return score, found


class ContentClassifier:
    """Classify job content quality and relevance."""
    
    @staticmethod
    def is_valid_description(text: Optional[str], min_length: int = 100) -> bool:
        """Check if description is substantial enough."""
        if not text:
            return False
        return len(str(text).strip()) >= min_length
    
    @staticmethod
    def is_relevant_source(source: Optional[str], accepted: List[str]) -> bool:
        """Check if job source is accepted."""
        if not source:
            return False
        source_lower = str(source).lower()
        return any(s in source_lower for s in accepted)
    
    @staticmethod
    def detect_remote_work(text: str) -> Tuple[bool, str]:
        """
        Detect if job is remote/hybrid/on-site.
        
        Returns:
            (is_remote: bool, mode: str)
        """
        text_lower = text.lower()
        
        if "remote" in text_lower:
            if "fully" in text_lower or "100" in text_lower:
                return True, "fully_remote"
            return True, "remote"
        elif "hybrid" in text_lower:
            return True, "hybrid"
        elif "on-site" in text_lower or "on site" in text_lower:
            return False, "on_site"
        
        return None, "unknown"


# ============================================================================
# Unified Feature Extractor Class
# ============================================================================

class UnifiedFeatureExtractor:
    """Single point of access for all feature extraction."""
    
    def __init__(self, cv_skills: Dict[str, int] = None):
        if cv_skills is None:
            cv_skills = CV_SKILLS
        
        self.skill_extractor = SkillExtractor(cv_skills)
        self.seniority_detector = SeniorityDetector()
        self.consulting_detector = ConsultingFitDetector()
        self.emerging_tech_detector = EmergingTechDetector()
        self.content_classifier = ContentClassifier()
    
    def extract_all(self, text: str, title: str = "") -> Dict:
        """
        Extract all features from job text.
        
        Returns comprehensive feature dictionary.
        """
        text_lower = text.lower()
        title_lower = title.lower()
        full_text = f"{title_lower} {text_lower}"
        
        # Extract skills
        extracted_skills = self.skill_extractor.extract(full_text)
        skill_weight = self.skill_extractor.get_skill_weights(extracted_skills)
        
        # Detect seniority
        seniority_level, seniority_name, seniority_conf = self.seniority_detector.detect(text_lower)
        
        # Consulting fit
        consulting_score, consulting_breakdown = self.consulting_detector.compute_consulting_fit_score(full_text)
        
        # Emerging tech
        emerging_score, emerging_list = self.emerging_tech_detector.detect(text_lower)
        
        # Work mode
        is_remote, work_mode = self.content_classifier.detect_remote_work(text_lower)
        
        return {
            "skills": {
                "extracted": extracted_skills,
                "weight_score": skill_weight,
                "count": len(extracted_skills),
            },
            "seniority": {
                "level": seniority_level,
                "name": seniority_name,
                "confidence": seniority_conf,
            },
            "consulting": {
                "fit_score": consulting_score,
                "keywords": consulting_breakdown["keywords"],
                "prestige_firm": consulting_breakdown["prestige_firm"],
                "strategic_skills": consulting_breakdown["strategic_skills"],
            },
            "emerging_tech": {
                "score": emerging_score,
                "technologies": emerging_list,
            },
            "work_mode": {
                "is_remote": is_remote,
                "mode": work_mode,
            },
        }
