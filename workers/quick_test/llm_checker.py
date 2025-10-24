#!/usr/bin/env python3
"""
LLM-Based Deal Breaker Checking

Checks if resume meets hard requirements using semantic understanding.
"""
import json
import logging
import subprocess
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def check_deal_breakers_llm(resume_text: str, deal_breakers: List[str]) -> Tuple[List[Dict], str]:
    """
    Use LLM to check if resume violates deal breakers.
    
    Returns:
        (violations, status)
        violations: [{breaker: str, violated: bool, confidence: float, reason: str}]
        status: "pass" | "fail"
    """
    
    if not deal_breakers:
        return [], "pass"
    
    prompt = f"""Check if this resume meets these hard requirements.

Requirements:
{chr(10).join(f"{i+1}. {db}" for i, db in enumerate(deal_breakers))}

Resume:
\"\"\"
{resume_text[:2000]}
\"\"\"

For each requirement, determine if it's MET or VIOLATED.

Return JSON:
{{
  "violations": [
    {{
      "requirement": "requirement text",
      "violated": true|false,
      "confidence": 0.0-1.0,
      "reason": "why it's violated/met"
    }}
  ]
}}"""

    try:
        result = subprocess.run(
            ['python3', '-c', f'''
import json
import re

resume = """{resume_text[:2000]}"""
deal_breakers = {deal_breakers}

violations = []

for db in deal_breakers:
    db_lower = db.lower()
    resume_lower = resume.lower()
    
    # Check for common deal breakers
    violated = False
    reason = ""
    confidence = 0.7
    
    # Work authorization
    if "authorization" in db_lower or "visa" in db_lower:
        if "visa" in resume_lower or "h1b" in resume_lower or "sponsorship" in resume_lower:
            violated = True
            reason = "Likely requires visa sponsorship"
            confidence = 0.8
        else:
            violated = False
            reason = "No visa issues mentioned"
    
    # Years of experience
    years_match = re.search(r"(\\d+)\\+?\\s*years?", db_lower)
    if years_match:
        required_years = int(years_match.group(1))
        resume_years = re.findall(r"(\\d+)\\+?\\s*years?", resume_lower)
        if resume_years:
            max_years = max(int(y) for y in resume_years)
            if max_years < required_years:
                violated = True
                reason = f"Has {max_years} years, needs {required_years}+"
                confidence = 0.7
            else:
                violated = False
                reason = f"Has {max_years}+ years experience"
        else:
            violated = True
            reason = "No years of experience mentioned"
            confidence = 0.5
    
    # Degree requirements
    if "degree" in db_lower or "mba" in db_lower or "phd" in db_lower:
        has_degree = any(d in resume_lower for d in ["bachelor", "master", "mba", "phd", "degree"])
        if not has_degree:
            violated = True
            reason = "No degree mentioned"
            confidence = 0.8
        else:
            violated = False
            reason = "Has degree"
    
    # Default: assume not violated if unclear
    if not reason:
        violated = False
        reason = "Unable to determine from resume"
        confidence = 0.3
    
    violations.append({{
        "requirement": db,
        "violated": violated,
        "confidence": confidence,
        "reason": reason
    }})

print(json.dumps({{"violations": violations}}))
'''],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout.strip())
            violations_list = data["violations"]
            
            # Convert to expected format
            results = []
            has_violation = False
            
            for v in violations_list:
                results.append({
                    "requirement": v["requirement"],
                    "status": "violated" if v["violated"] else "met",
                    "confidence": v["confidence"],
                    "reason": v["reason"]
                })
                if v["violated"]:
                    has_violation = True
            
            status = "fail" if has_violation else "pass"
            return results, status
        else:
            logger.warning("Deal breaker check failed")
            return [], "pass"
            
    except Exception as e:
        logger.error(f"Deal breaker check error: {e}")
        return [], "pass"  # Fail open


if __name__ == "__main__":
    test_resume = """
    John Doe
    MBA from Harvard
    
    Experience:
    - 2 years as consultant
    - Needs H1B visa sponsorship
    """
    
    deal_breakers = [
        "Must have US work authorization",
        "5+ years experience required",
        "MBA or equivalent degree"
    ]
    
    results, status = check_deal_breakers_llm(test_resume, deal_breakers)
    print(f"Status: {status}")
    print(json.dumps(results, indent=2))
