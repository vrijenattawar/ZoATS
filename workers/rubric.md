# Rubric Generator (Worker)
Status: Draft | Owner: con_Sq70IglhvzX4GJE3

Purpose
- Convert a Job Description (JD) and optional founder notes into a structured rubric with weighted criteria and scoring bands, plus deal-breakers.

Inputs
- jobs/<job>/job-description.md
- Optional: jobs/<job>/founder-notes.md

Outputs
- jobs/<job>/rubric.json (criteria, weights sum=100, bands)
- jobs/<job>/rubric.md (human-readable)
- jobs/<job>/deal_breakers.json

Interface
- `python workers/rubric/main.py --jd jobs/<job>/job-description.md --out jobs/<job>/rubric.json [--founder-notes jobs/<job>/founder-notes.md] [--interactive | --non-interactive] --dry-run`

Tonight Milestones
- Non-interactive JD→rubric: rubric.json + rubric.md
- Optional: minimal interactive prompts

Definition of Done (Night 1)
- Valid JSON written, weights sum to 100, at least 5 criteria, deal-breakers supported
- MD summary present and readable

Dependencies
- None (reads local files)

Risks & Mitigations
- Over-complex rubrics → start with Must/Should/Nice; document assumptions

Checklist (Night 1)
- [ ] Parse JD into key requirements
- [ ] Draft criteria and weights
- [ ] Emit rubric.json, rubric.md, deal_breakers.json
- [ ] Verify totals and file existence

Paths
- jobs/<job>/

Integration Points
- Scoring Engine consumes rubric.json and deal_breakers.json

Notes
- Socratic flow optional; keep prompts minimal tonight
