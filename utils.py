"""
Utility Functions and Helpers
"""

import logging
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)


class ScoringResultRanker:
    """Rank and filter scoring results."""
    
    @staticmethod
    def rank_by_score(results: List[Dict], ascending: bool = False) -> List[Dict]:
        """
        Rank results by final score.
        
        Args:
            results: List of scoring results
            ascending: If True, lowest scores first
        
        Returns:
            Sorted list
        """
        return sorted(
            results,
            key=lambda x: x.get("final_score", 0),
            reverse=not ascending
        )
    
    @staticmethod
    def filter_by_threshold(results: List[Dict], threshold: float = 0.5) -> List[Dict]:
        """
        Filter results by minimum score.
        
        Args:
            results: List of scoring results
            threshold: Minimum score (0-1)
        
        Returns:
            Filtered list
        """
        return [r for r in results if r.get("final_score", 0) >= threshold]
    
    @staticmethod
    def filter_by_skill(results: List[Dict], required_skills: List[str]) -> List[Dict]:
        """
        Filter results that contain specific skills.
        
        Args:
            results: List of scoring results
            required_skills: Skills that must be detected
        
        Returns:
            Filtered list
        """
        filtered = []
        for result in results:
            detected = set(result.get("skills_detected", []))
            required = set(s.lower() for s in required_skills)
            
            if required.issubset(detected):
                filtered.append(result)
        
        return filtered
    
    @staticmethod
    def filter_by_seniority(results: List[Dict], required_level: str) -> List[Dict]:
        """
        Filter results by detected seniority level.
        
        Args:
            results: List of scoring results
            required_level: Required seniority (e.g., "senior")
        
        Returns:
            Filtered list
        """
        return [
            r for r in results
            if r.get("seniority", "").lower() == required_level.lower()
        ]
    
    @staticmethod
    def filter_consulting_only(results: List[Dict]) -> List[Dict]:
        """Filter to consulting opportunities only."""
        return [r for r in results if r.get("is_consulting_opportunity", False)]


class ScoreExporter:
    """Export scoring results in various formats."""
    
    @staticmethod
    def to_csv_compatible(results: List[Dict]) -> str:
        """
        Convert results to CSV-compatible format.
        
        Returns single CSV line per job
        """
        if not results:
            return ""
        
        lines = []
        for result in results:
            if not result.get("success", False):
                continue
            
            line = (
                f"{result.get('title', 'N/A')},"
                f"{result.get('company', 'N/A')},"
                f"{result.get('final_score', 0):.3f},"
                f"{result.get('seniority', 'unknown')},"
                f"{','.join(result.get('skills_detected', [])[:3])}"
            )
            lines.append(line)
        
        return "\n".join(lines)
    
    @staticmethod
    def to_json(results: List[Dict], pretty: bool = True) -> str:
        """Export as JSON."""
        if pretty:
            return json.dumps(results, indent=2, ensure_ascii=False)
        return json.dumps(results, ensure_ascii=False)
    
    @staticmethod
    def to_markdown_report(results: List[Dict]) -> str:
        """
        Create markdown report of top matches.
        
        Useful for documentation/sharing
        """
        lines = ["# Job Scoring Report\n"]
        
        # Statistics
        total = len(results)
        successful = sum(1 for r in results if r.get("success", False))
        avg_score = sum(r.get("final_score", 0) for r in results if r.get("success")) / successful if successful > 0 else 0
        
        lines.append(f"**Total Jobs:** {total}\n")
        lines.append(f"**Successfully Scored:** {successful}\n")
        lines.append(f"**Average Score:** {avg_score:.3f}\n\n")
        
        # Top results
        lines.append("## Top Opportunities\n")
        top_results = sorted(
            [r for r in results if r.get("success", False)],
            key=lambda x: x.get("final_score", 0),
            reverse=True
        )[:10]
        
        for i, result in enumerate(top_results, 1):
            lines.append(f"### {i}. {result.get('title', 'Unknown')}\n")
            lines.append(f"- **Score:** {result.get('final_score', 0):.1%}\n")
            lines.append(f"- **Company:** {result.get('company', 'N/A')}\n")
            lines.append(f"- **Seniority:** {result.get('seniority', 'unknown')}\n")
            lines.append(f"- **Key Reason:** {result.get('top_reason', 'No reason')}\n")
            lines.append(f"- **Skills Detected:** {', '.join(result.get('skills_detected', [])[:5])}\n")
            lines.append("")
        
        return "\n".join(lines)


class ConfigValidator:
    """Validate and manage scoring configuration."""
    
    @staticmethod
    def validate_weights(weights: Dict[str, float]) -> bool:
        """
        Validate scoring weights.
        
        Rules:
        - All dimension weights present
        - All weights 0-1
        - Sum to 1.0
        """
        expected_keys = {
            "skill_matching",
            "consulting_fit",
            "seniority_match",
            "semantic_relevance",
            "growth_potential",
            "cultural_alignment",
        }
        
        if set(weights.keys()) != expected_keys:
            logger.error(f"Missing weights. Expected: {expected_keys}")
            return False
        
        for key, value in weights.items():
            if not (0 <= value <= 1):
                logger.error(f"Weight {key} out of range: {value}")
                return False
        
        total = sum(weights.values())
        if not (0.99 <= total <= 1.01):  # Allow small floating point error
            logger.error(f"Weights don't sum to 1.0: {total}")
            return False
        
        return True


class PerformanceMonitor:
    """Monitor API performance metrics."""
    
    def __init__(self):
        self.scores_computed = 0
        self.total_time = 0
        self.errors = 0
    
    def record_score(self, execution_time: float, success: bool = True):
        """Record a scoring operation."""
        self.scores_computed += 1
        self.total_time += execution_time
        
        if not success:
            self.errors += 1
    
    def get_stats(self) -> Dict:
        """Get performance statistics."""
        avg_time = self.total_time / self.scores_computed if self.scores_computed > 0 else 0
        
        return {
            "total_scores": self.scores_computed,
            "total_time_seconds": round(self.total_time, 2),
            "average_time_per_score": round(avg_time, 3),
            "errors": self.errors,
            "success_rate": round(100 * (1 - self.errors / self.scores_computed), 2) if self.scores_computed > 0 else 0,
        }


# Global monitor instance
performance_monitor = PerformanceMonitor()
