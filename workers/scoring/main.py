#!/usr/bin/env python3
"""
Scoring Engine (Night 1 stub)
- Applies simple heuristics to produce quick_test.json and scores.json
- Never fails hard; logs missing inputs and proceeds with defaults
"""
import argparse, json, logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception as e:
        logger.warning(f"Failed to read JSON {path}: {e}")
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--job", required=True)
    p.add_argument("--candidate", required=True)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    root = Path(__file__).resolve().parents[2]  # ZoATS/
    cdir = root / "jobs" / args.job / "candidates" / args.candidate
    parsed_dir = cdir / "parsed"
    out_dir = cdir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)

    rubric = load_json(root / "jobs" / args.job / "rubric.json") or {"criteria": []}
    deals = load_json(root / "jobs" / args.job / "deal_breakers.json") or {"rules": []}
    fields = load_json(parsed_dir / "fields.json") or {}
    text_md = (parsed_dir / "text.md").read_text() if (parsed_dir / "text.md").exists() else ""

    # Quick-test: trivial heuristic - fail if email missing or resume text very short
    quick = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "rules": [],
        "status": "pass",
        "reasons": []
    }
    if not fields.get("email"):
        quick["rules"].append("missing_email")
        quick["status"] = "flag"
        quick["reasons"].append("Email not detected in parsed fields")
    if len(text_md.strip()) < 50:
        quick["rules"].append("short_resume_text")
        quick["status"] = "flag" if quick["status"] == "pass" else quick["status"]
        quick["reasons"].append("Resume text appears very short")

    # Scores: assign 0 by default for criteria; presence-based +10 simple bump
    scores = {"total": 0, "criteria": []}
    for crit in rubric.get("criteria", []):
        name = crit.get("name", "criterion")
        weight = crit.get("weight", 0)
        score = 0
        # naive: if any keyword present in text, give half of weight
        kws = [k.lower() for k in crit.get("keywords", [])]
        if kws and any(k in text_md.lower() for k in kws):
            score = max(1, int(0.5 * weight))
        scores["criteria"].append({"name": name, "weight": weight, "score": score})
        scores["total"] += score

    if args.dry_run:
        logger.info("[dry-run] would write quick_test.json and scores.json")
        return 0

    (out_dir / "quick_test.json").write_text(json.dumps(quick, indent=2))
    (out_dir / "scores.json").write_text(json.dumps(scores, indent=2))
    logger.info("✓ Scoring complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
