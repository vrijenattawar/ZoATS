#!/usr/bin/env python3
"""Resume Parser Worker - Extract text and fields from candidate resumes."""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)sZ %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from PDF with multiple fallback strategies."""
    strategies = []
    
    # Strategy 1: pdfminer.six (best quality)
    try:
        from pdfminer.high_level import extract_text
        logger.info(f"[PDF] Trying pdfminer.six for {pdf_path.name}")
        text = extract_text(str(pdf_path))
        if text and len(text.strip()) > 0:
            logger.info(f"[PDF] ✓ pdfminer.six extracted {len(text)} chars")
            return text.strip()
        strategies.append("pdfminer.six (no text)")
    except Exception as e:
        strategies.append(f"pdfminer.six ({type(e).__name__})")
        logger.debug(f"[PDF] pdfminer.six failed: {e}")
    
    # Strategy 2: pypdf
    try:
        import pypdf
        logger.info(f"[PDF] Trying pypdf for {pdf_path.name}")
        reader = pypdf.PdfReader(str(pdf_path))
        text = ""
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text and len(text.strip()) > 0:
            logger.info(f"[PDF] ✓ pypdf extracted {len(text)} chars from {len(reader.pages)} page(s)")
            return text.strip()
        strategies.append("pypdf (no text)")
    except Exception as e:
        strategies.append(f"pypdf ({type(e).__name__})")
        logger.debug(f"[PDF] pypdf failed: {e}")
    
    # Strategy 3: PyPDF2 (legacy)
    try:
        import PyPDF2
        logger.info(f"[PDF] Trying PyPDF2 for {pdf_path.name}")
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text and len(text.strip()) > 0:
            logger.info(f"[PDF] ✓ PyPDF2 extracted {len(text)} chars")
            return text.strip()
        strategies.append("PyPDF2 (no text)")
    except Exception as e:
        strategies.append(f"PyPDF2 ({type(e).__name__})")
        logger.debug(f"[PDF] PyPDF2 failed: {e}")
    
    # Strategy 4: pdfplumber (optional, best for tables)
    try:
        import pdfplumber
        logger.info(f"[PDF] Trying pdfplumber for {pdf_path.name}")
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text and len(text.strip()) > 0:
            logger.info(f"[PDF] ✓ pdfplumber extracted {len(text)} chars")
            return text.strip()
        strategies.append("pdfplumber (no text)")
    except ImportError:
        strategies.append("pdfplumber (not installed)")
    except Exception as e:
        strategies.append(f"pdfplumber ({type(e).__name__})")
        logger.debug(f"[PDF] pdfplumber failed: {e}")
    
    # All strategies failed
    logger.error(f"[PDF] All extraction strategies failed for {pdf_path.name}")
    logger.error(f"[PDF] Tried: {', '.join(strategies)}")
    
    # Check if file is valid PDF
    try:
        with open(pdf_path, 'rb') as f:
            header = f.read(8)
            if not header.startswith(b'%PDF'):
                logger.error(f"[PDF] File does not have valid PDF header: {header[:20]}")
                return ""
    except Exception as e:
        logger.error(f"[PDF] Could not read file header: {e}")
    
    return ""


def extract_docx_text(docx_path: Path) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(docx_path)
        paragraphs = [p.text for p in doc.paragraphs]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        return ""


def extract_md_text(md_path: Path) -> str:
    """Read markdown file directly."""
    try:
        return md_path.read_text(encoding='utf-8').strip()
    except Exception as e:
        logger.error(f"Markdown reading failed: {e}")
        return ""


def extract_text_from_file(file_path: Path) -> str:
    """Detect file type and extract text."""
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        logger.info(f"Extracting PDF: {file_path}")
        return extract_pdf_text(file_path)
    elif suffix == '.docx':
        logger.info(f"Extracting DOCX: {file_path}")
        return extract_docx_text(file_path)
    elif suffix in ['.md', '.markdown']:
        logger.info(f"Reading markdown: {file_path}")
        return extract_md_text(file_path)
    else:
        logger.warning(f"Unsupported file type: {suffix}")
        return ""


def extract_email(text: str) -> Optional[str]:
    """Best-effort email extraction using regex."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None


def extract_name(text: str) -> Optional[str]:
    """Best-effort name extraction from first few lines."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return None
    
    # Simple heuristic: first non-empty line that looks like a name
    # (short, mostly letters, capitalized)
    for line in lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and len(line) < 50:
            if all(word[0].isupper() for word in words if word):
                return line
    
    return lines[0] if lines else None


def estimate_years_experience(text: str) -> Optional[int]:
    """Heuristic years of experience estimation."""
    # Look for explicit mentions like "5 years", "5+ years", etc.
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                return int(matches[0])
            except:
                pass
    
    # Fallback: count year ranges (YYYY-YYYY or YYYY-Present)
    date_ranges = re.findall(r'(20\d{2})\s*[-–—]\s*(20\d{2}|present)', text, re.IGNORECASE)
    if date_ranges:
        total_years = 0
        for start, end in date_ranges:
            start_year = int(start)
            end_year = 2025 if end.lower() == 'present' else int(end)
            total_years += max(0, end_year - start_year)
        return min(total_years, 50)  # Cap at reasonable maximum
    
    return None


def extract_fields(text: str) -> Dict:
    """Extract structured fields from text using heuristics."""
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "years_experience": estimate_years_experience(text),
    }


def parse_resume(job: str, candidate_id: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Main parsing logic for a candidate's resume."""
    base_path = Path("/home/workspace/ZoATS")
    candidate_dir = base_path / "jobs" / job / "candidates" / candidate_id
    raw_dir = candidate_dir / "raw"
    parsed_dir = candidate_dir / "parsed"
    
    # Find resume file
    if not raw_dir.exists():
        return False, f"Raw directory not found: {raw_dir}"
    
    resume_files = list(raw_dir.glob("*.[pP][dD][fF]")) + \
                   list(raw_dir.glob("*.[dD][oO][cC][xX]")) + \
                   list(raw_dir.glob("*.[mM][dD]"))
    
    if not resume_files:
        return False, f"No resume file found in {raw_dir}"
    
    resume_file = resume_files[0]
    logger.info(f"Processing: {resume_file}")
    
    # Validate file exists and has content
    if not resume_file.exists():
        return False, f"File not found: {resume_file}"
    
    file_size = resume_file.stat().st_size
    if file_size == 0:
        return False, f"File is empty: {resume_file}"
    
    logger.info(f"File size: {file_size} bytes")
    
    # Extract text
    text = extract_text_from_file(resume_file)
    if not text:
        return False, f"Failed to extract text from {resume_file}"
    
    # Log sample for debugging
    sample = text[:200].replace('\n', ' ')
    logger.info(f"Text sample: {sample}...")
    
    # Extract fields
    fields = extract_fields(text)
    logger.info(f"Extracted fields: {fields}")
    
    if dry_run:
        logger.info("[DRY RUN] Would write:")
        logger.info(f"  - {parsed_dir / 'text.md'} ({len(text)} chars)")
        logger.info(f"  - {parsed_dir / 'fields.json'}")
        return True, "Dry run successful"
    
    # Write outputs
    parsed_dir.mkdir(parents=True, exist_ok=True)
    
    text_file = parsed_dir / "text.md"
    text_file.write_text(text, encoding='utf-8')
    logger.info(f"✓ Wrote: {text_file} ({len(text)} chars)")
    
    fields_file = parsed_dir / "fields.json"
    fields_file.write_text(json.dumps(fields, indent=2), encoding='utf-8')
    logger.info(f"✓ Wrote: {fields_file}")
    
    # Verify outputs
    if not text_file.exists() or text_file.stat().st_size == 0:
        return False, "text.md is missing or empty"
    
    if not fields_file.exists():
        return False, "fields.json is missing"
    
    return True, "Parsing complete"


def main(job: str, candidate_id: str, dry_run: bool = False) -> int:
    """Entry point for resume parser."""
    try:
        success, message = parse_resume(job, candidate_id, dry_run)
        if success:
            logger.info(f"✓ {message}")
            return 0
        else:
            logger.error(f"✗ {message}")
            return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume Parser Worker")
    parser.add_argument("--job", required=True, help="Job ID")
    parser.add_argument("--candidate", required=True, help="Candidate ID")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    
    args = parser.parse_args()
    sys.exit(main(args.job, args.candidate, args.dry_run))
