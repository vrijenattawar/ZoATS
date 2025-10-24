#!/usr/bin/env python3
"""
ZoATS Gestalt System Smoke Test
End-to-end validation for mckinsey-associate-15264
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

JOB_ID = "mckinsey-associate-15264"
CANDIDATES = ["vrijen", "whitney", "sample1", "marla"]
VALID_DECISIONS = ["STRONG_INTERVIEW", "INTERVIEW", "MAYBE", "PASS"]
BASE_PATH = Path("/home/workspace/ZoATS/jobs")


class TestFailure(Exception):
    """Test failure exception"""
    pass


def verify_file_exists(path: Path, description: str) -> bool:
    """Verify file exists and is non-empty"""
    if not path.exists():
        raise TestFailure(f"Missing: {description} at {path}")
    
    if path.stat().st_size == 0:
        raise TestFailure(f"Empty file: {description} at {path}")
    
    logger.info(f"✓ {description} exists ({path.stat().st_size} bytes)")
    return True


def verify_gestalt_evaluation(path: Path, candidate: str) -> Dict:
    """Verify gestalt_evaluation.json is valid and complete"""
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise TestFailure(f"Invalid JSON in {candidate} gestalt_evaluation: {e}")
    
    # Required fields
    required_fields = [
        "decision", "confidence", "key_strengths", "concerns",
        "overall_narrative", "interview_focus", "elite_signals",
        "business_impact", "ai_detection"
    ]
    
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise TestFailure(f"{candidate}: Missing fields in gestalt: {missing}")
    
    # Validate decision
    decision = data.get("decision")
    if decision not in VALID_DECISIONS:
        raise TestFailure(
            f"{candidate}: Invalid decision '{decision}'. "
            f"Expected one of {VALID_DECISIONS}"
        )
    
    # Validate confidence
    confidence = data.get("confidence")
    if confidence not in ["high", "medium", "low"]:
        raise TestFailure(
            f"{candidate}: Invalid confidence '{confidence}'. "
            f"Expected high/medium/low"
        )
    
    logger.info(
        f"✓ {candidate}: Valid gestalt ({decision}, {confidence} confidence)"
    )
    return data


def verify_dossier(path: Path, candidate: str) -> None:
    """Verify dossier.md exists and has content"""
    content = path.read_text()
    
    # Check for key sections
    required_sections = [
        "# Candidate Dossier",
        "## Executive Summary",
        "## Key Strengths",
        "## Concerns"
    ]
    
    missing_sections = [s for s in required_sections if s not in content]
    if missing_sections:
        logger.warning(
            f"{candidate}: Dossier missing sections: {missing_sections}"
        )
    
    if len(content) < 500:
        logger.warning(
            f"{candidate}: Dossier seems short ({len(content)} chars)"
        )
    
    logger.info(f"✓ {candidate}: Valid dossier ({len(content)} chars)")


def collect_decision_distribution(evaluations: Dict[str, Dict]) -> Dict[str, int]:
    """Collect decision distribution across candidates"""
    distribution = {d: 0 for d in VALID_DECISIONS}
    
    for candidate, data in evaluations.items():
        decision = data.get("decision")
        if decision:
            distribution[decision] += 1
    
    return distribution


def main() -> int:
    """Run smoke test"""
    logger.info(f"Starting smoke test for job {JOB_ID}")
    logger.info(f"Testing {len(CANDIDATES)} candidates: {', '.join(CANDIDATES)}")
    
    job_path = BASE_PATH / JOB_ID
    if not job_path.exists():
        logger.error(f"Job directory not found: {job_path}")
        return 1
    
    failures = []
    evaluations = {}
    
    # Test each candidate
    for candidate in CANDIDATES:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing candidate: {candidate}")
        logger.info(f"{'='*60}")
        
        candidate_path = job_path / "candidates" / candidate
        
        try:
            # Check directory exists
            if not candidate_path.exists():
                raise TestFailure(f"Candidate directory not found: {candidate_path}")
            
            # Check outputs directory
            outputs_path = candidate_path / "outputs"
            verify_file_exists(outputs_path, f"{candidate} outputs directory")
            
            # Check gestalt_evaluation.json
            gestalt_path = outputs_path / "gestalt_evaluation.json"
            verify_file_exists(gestalt_path, f"{candidate} gestalt_evaluation.json")
            gestalt_data = verify_gestalt_evaluation(gestalt_path, candidate)
            evaluations[candidate] = gestalt_data
            
            # Check dossier.md
            dossier_path = outputs_path / "dossier.md"
            verify_file_exists(dossier_path, f"{candidate} dossier.md")
            verify_dossier(dossier_path, candidate)
            
            logger.info(f"✓ {candidate}: ALL CHECKS PASSED")
            
        except TestFailure as e:
            logger.error(f"✗ {candidate}: {e}")
            failures.append((candidate, str(e)))
        except Exception as e:
            logger.error(f"✗ {candidate}: Unexpected error: {e}", exc_info=True)
            failures.append((candidate, f"Unexpected error: {e}"))
    
    # Decision distribution analysis
    logger.info(f"\n{'='*60}")
    logger.info("DECISION DISTRIBUTION")
    logger.info(f"{'='*60}")
    
    distribution = collect_decision_distribution(evaluations)
    for decision, count in distribution.items():
        logger.info(f"{decision:20s}: {count}")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")
    
    passed = len(CANDIDATES) - len(failures)
    logger.info(f"Candidates tested: {len(CANDIDATES)}")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {len(failures)}")
    
    if failures:
        logger.error("\nFAILURES:")
        for candidate, error in failures:
            logger.error(f"  {candidate}: {error}")
        return 1
    
    logger.info("\n✓ ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
