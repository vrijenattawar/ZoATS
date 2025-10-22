# N5 ATS for Zo Computer

**AI-Powered Applicant Tracking System for Hiring Teams**

## Overview

N5 ATS is a complete hiring workflow system built for Zo Computer. It automates candidate intake, resume parsing, scoring, and pipeline management using AI-assisted workflows.

## Quick Start

```bash
curl -sSL https://raw.githubusercontent.com/vrijenattawar/n5-ats/main/install.sh | bash
```

## Core Features

### 📥 **Candidate Intake**
- Email-based application processing
- Resume parsing and data extraction
- Automatic candidate profile generation
- Multi-format support (PDF, DOCX, TXT)

### 🎯 **Job Management**
- Job requisition tracking
- Web scraping from job boards
- URL-based job import
- Rubric-based candidate scoring

### 🤖 **AI Workers**
- **Parser**: Extract structured data from resumes
- **Scorer**: Evaluate candidates against job criteria
- **Dossier**: Generate comprehensive candidate summaries
- **Intake**: Process inbound applications

### 📊 **Pipeline Orchestration**
- Automated candidate workflow
- Status tracking (new → screening → interview → offer)
- Batch processing capabilities
- Interaction history logging

## System Architecture

```
ZoATS/
├── workers/          # AI processing workers
├── pipeline/         # Orchestration engine
├── jobs/            # Job + candidate data
│   └── {job-id}/
│       └── candidates/
│           └── {candidate-id}/
│               ├── raw/         # Original resume
│               ├── parsed/      # Extracted data
│               ├── outputs/     # Generated profiles
│               └── interactions.md
├── commands/        # ATS commands
├── scripts/         # Automation scripts
├── schemas/         # Data validation
└── config/          # Configuration
```

## Dependencies

**Requires**: [N5 Core](https://github.com/vrijenattawar/n5-core) (installed automatically)

N5 ATS builds on N5 Core's foundation:
- Session state management
- Safety validation
- Schema validation framework
- Command registry system

## Installation

### Standard Install
```bash
curl -sSL https://raw.githubusercontent.com/vrijenattawar/n5-ats/main/install.sh | bash
```

### Manual Install
```bash
# 1. Install n5-core first
curl -sSL https://raw.githubusercontent.com/vrijenattawar/n5-core/main/install.sh | bash

# 2. Clone n5-ats
cd /home/workspace
git clone https://github.com/vrijenattawar/ZoATS.git ZoATS

# 3. Configure
cp ZoATS/config/settings.example.json ZoATS/config/settings.json
```

## Usage Examples

### Process Candidate Email
```bash
# Candidate sends resume to your intake email
# Worker automatically:
# 1. Extracts resume attachment
# 2. Parses candidate data
# 3. Creates candidate profile
# 4. Assigns to job based on content
```

### Add Job Posting
```bash
# Use command: job-add
# Provide job URL
# System extracts and stores job details
```

### Score Candidates
```bash
# Use command: candidate-score
# System evaluates candidates against job rubric
# Generates scores and recommendations
```

## Configuration

Edit `ZoATS/config/settings.json`:

```json
{
  "intake_email": "jobs@yourcompany.zo.computer",
  "default_job_status": "open",
  "scoring": {
    "enabled": true,
    "auto_score_threshold": 70
  },
  "notifications": {
    "slack_webhook": "",
    "email_alerts": true
  }
}
```

## Data Schemas

- **Candidate**: `schemas/candidate.schema.json`
- **Job**: `schemas/job.schema.json`
- See `/schemas/` for complete validation rules

## Commands

| Command | Description |
|---------|-------------|
| `jobs-add` | Add single job manually |
| `jobs-scrape` | Scrape jobs from company list |
| `job-add` | Import job from URL |
| `candidate-intake` | Process new candidate |
| `candidate-score` | Score candidate vs rubric |
| `pipeline-run` | Run full processing pipeline |

## Development

### Adding Custom Workers
```bash
# 1. Create worker in workers/
# 2. Follow worker protocol (see WORKERS_PROTOCOL.md)
# 3. Register in pipeline/run.py
```

### Extending Schemas
```bash
# Edit schemas/*.schema.json
# Validate with: n5_schema_validation.py
```

## Ethics & Principles

N5 ATS follows ethical hiring practices:
- Bias detection and mitigation
- Privacy-first data handling
- Transparent scoring criteria
- GDPR/compliance ready

See `docs/ETHICS_AND_PRINCIPLES.md` for full guidelines.

## Roadmap

See `docs/ROADMAP.md` for planned features.

## Support

- **Issues**: [GitHub Issues](https://github.com/vrijenattawar/ZoATS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vrijenattawar/ZoATS/discussions)
- **Zo Community**: [Discord](https://discord.gg/zocomputer)

## License

MIT

---

**Built on [N5 Core](https://github.com/vrijenattawar/n5-core)** | **Powered by [Zo Computer](https://zo.computer)**
