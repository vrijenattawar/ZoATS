#!/usr/bin/env python3
"""
Zo LLM Signal Extraction

This module is designed to be called from Zo's environment where LLM tools are available.
It extracts signals using real LLM calls, not heuristics.
"""
import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def extract_signals_with_zo_llm(resume_text: str, job_context: str = "management consulting") -> Dict:
    """
    Extract signals using Zo's LLM. Must be called from Zo environment.
    
    Returns dict matching ExtractionResult schema.
    """
    
    prompt = f"""Extract structured signals from this resume for a {job_context} role.

RESUME:
{resume_text[:4000]}

Return JSON with:
{{
  "business_impact": [
    {{"value": 90, "type": "revenue", "context": "generated $90M in sales", "confidence": 0.9}}
  ],
  "elite_signals": [
    {{"type": "top_tier_mba", "detail": "Cornell MBA", "boost_factor": 1.15}},
    {{"type": "elite_company", "detail": "McKinsey", "boost_factor": 1.4}},
    {{"type": "acceptance_rate", "detail": "4% acceptance", "boost_factor": 1.3}}
  ],
  "consulting_experience": {{
    "has_direct": true,
    "years": 4,
    "firms": ["Deloitte Consulting"],
    "confidence": 0.9
  }},
  "role_match": {{
    "fit_score": 0.85,
    "reasons": ["consulting experience", "quantitative background"],
    "concerns": ["no direct industry experience"]
  }},
  "red_flags": []
}}

RULES:
- Business impact: extract $ amounts, growth %, scale
- Elite signals:
  * Top MBAs: H/W/S/MIT = 1.3, Cornell/Dartmouth/Columbia = 1.15
  * MBB: McKinsey/Bain/BCG = 1.4
  * Tier 2 consulting: Deloitte/Accenture = 1.2
  * FAANG: Google/Meta/Amazon = 1.15
  * Selective programs: <5% acceptance = 1.3
- Consulting: ONLY real consulting roles, NOT volunteer
- Red flags: ["retail only", "no business exp", "job hopping"]
- fit_score: 0.9+ exceptional, 0.7-0.9 strong, 0.5-0.7 moderate, <0.5 weak

Return ONLY valid JSON."""

    try:
        # This will be called from gestalt_scorer which runs in my context
        import anthropic
        
        # Create client using environment variable
        client = anthropic.Anthropic()
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text
        
        # Clean markdown fences
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        data = json.loads(response.strip())
        logger.info("✓ LLM extraction successful")
        
        return data
        
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        # Return minimal structure
        return {
            "business_impact": [],
            "elite_signals": [],
            "consulting_experience": {"has_direct": False, "years": 0, "firms": [], "confidence": 0.5},
            "role_match": {"fit_score": 0.3, "reasons": [], "concerns": ["extraction failed"]},
            "red_flags": []
        }
