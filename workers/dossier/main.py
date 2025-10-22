#!/usr/bin/env python3
"""
Dossier Generator (Night 1 stub)
- Composes candidate.md from parsed fields and scoring outputs
"""
import argparse, json, logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)sZ %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def read_json(p: Path):
    if not p.exists(): return None
    try:
        return json.loads(p.read_text())
    except Exception as e:
        logger.warning(f"Could not read {p}: {e}")
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    cdir = root / "jobs" / args.job / "candidates" / args.candidate
    parsed = cdir / "parsed"
    outputs = cdir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)

    fields = read_json(parsed / "fields.json") or {}
    quick = read_json(outputs / "quick_test.json") or {"status": "unknown", "reasons": []}
    scores = read_json(outputs / "scores.json") or {"total": 0, "criteria": []}

    lines = []
    lines.append(f"# Candidate Summary — {args.candidate}")
    lines.append("")
    lines.append(f"- Generated: {datetime.utcnow().isoformat()}Z")
    lines.append(f"- Job: {args.job}")
    lines.append(f"- Quick Test: {quick.get('status')}")
    if quick.get("reasons"): lines.append(f"- Reasons: {', '.join(quick['reasons'])}")
    name = fields.get("name") or "(unknown)"
    email = fields.get("email") or "(unknown)"
    lines.append(f"- Name: {name}")
    lines.append(f"- Email: {email}")
    lines.append("")
    lines.append("## Scores")
    lines.append(f"Total: {scores.get('total', 0)}")
    for c in scores.get("criteria", []):
        lines.append(f"- {c.get('name')}: {c.get('score', 0)} / weight {c.get('weight', 0)}")
    lines.append("")
    lines.append("## Next Questions")
    lines.append("- …")

    if args.dry_run:
        logger.info("[dry-run] would write outputs/candidate.md and outputs/candidate.json")
        return 0

    (outputs / "candidate.md").write_text("\n".join(lines))
    (outputs / "candidate.json").write_text(json.dumps({
        "job": args.job,
        "candidate": args.candidate,
        "quick": quick,
        "scores": scores,
        "fields": fields,
    }, indent=2))
    logger.info("✓ Dossier written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
