"""Report generation tool"""
import logging
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)


def generate_report(
    topic: str,
    findings: List[Dict],
    summary: str,
    conclusion: str
) -> Dict:
    """
    Generate a comprehensive report.
    
    Args:
        topic: Research topic
        findings: List of findings
        summary: Research summary
        conclusion: Research conclusion
        
    Returns:
        Report dictionary
    """
    logger.info(f"Generating report for topic: {topic}")
    
    return {
        "topic": topic,
        "summary": summary,
        "findings": findings,
        "conclusion": conclusion,
        "generated_at": datetime.now().isoformat(),
    }
