"""
Core NLP processing for resumes.

Uses lightweight, dependency-free techniques (regex + NLTK tokenization +
keyword/phrase matching) rather than heavyweight downloaded language models,
so the project runs fully offline once installed.
"""
import re
from collections import Counter

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from .skills_data import (
    ALL_SKILLS,
    SECTION_SYNONYMS,
    DEGREE_KEYWORDS,
    ACTION_VERBS,
    WEAK_PHRASES,
)

# Ensure required NLTK corpora are present (downloaded once, cached locally).
for pkg in ("punkt", "punkt_tab", "stopwords"):
    try:
        nltk.data.find(f"tokenizers/{pkg}" if "punkt" in pkg else f"corpora/{pkg}")
    except LookupError:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}")
LINKEDIN_RE = re.compile(r"(linkedin\.com/[^\s,)]+)", re.IGNORECASE)
GITHUB_RE = re.compile(r"(github\.com/[^\s,)]+)", re.IGNORECASE)
YEAR_RANGE_RE = re.compile(r"(19|20)\d{2}\s*(-|to|–)\s*((19|20)\d{2}|present|current)", re.IGNORECASE)

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    STOPWORDS = set()


def clean_text(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize(text):
    try:
        tokens = word_tokenize(text.lower())
    except LookupError:
        tokens = re.findall(r"[a-zA-Z][a-zA-Z+.#-]*", text.lower())
    return [t for t in tokens if t.isalpha() and t not in STOPWORDS and len(t) > 1]


def extract_contact_info(text):
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)
    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0).strip() if phone else None,
        "linkedin": linkedin.group(1) if linkedin else None,
        "github": github.group(1) if github else None,
    }


def detect_sections(text):
    """Return dict of section_name -> bool(found) based on header synonyms."""
    lower = text.lower()
    found = {}
    for section, synonyms in SECTION_SYNONYMS.items():
        found[section] = any(
            re.search(rf"(?:^|\n)\s*{re.escape(syn)}\s*[:\n]", lower) or syn in lower
            for syn in synonyms
        )
    return found


def extract_skills(text):
    """Match known skills as whole phrases/words against resume text."""
    lower = f" {text.lower()} "
    found = []
    for skill in ALL_SKILLS:
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, lower):
            found.append(skill)
    return sorted(set(found))


def extract_education(text):
    lower = f" {text.lower()} "
    found = []
    for deg in DEGREE_KEYWORDS:
        token = deg.strip()
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(token) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, lower):
            found.append(token)
    return sorted(set(found))


def estimate_experience_years(text):
    """Estimate total years of experience from date ranges like 2019-2022."""
    matches = YEAR_RANGE_RE.findall(text)
    years_found = []
    for m in re.finditer(YEAR_RANGE_RE, text):
        span = m.group(0)
        nums = re.findall(r"(19|20)\d{2}", span)
        start_match = re.search(r"(19|20)\d{2}", span)
        if "present" in span.lower() or "current" in span.lower():
            import datetime
            end = datetime.date.today().year
        else:
            end_match = re.findall(r"(19|20)\d{2}", span)
            end = int(span[-4:]) if span[-4:].isdigit() else None
        if start_match:
            start = int(start_match.group(0))
            try:
                if end and end >= start:
                    years_found.append(end - start)
            except Exception:
                pass
    return sum(years_found) if years_found else 0


def count_action_verbs(text):
    lower = text.lower()
    counts = Counter()
    for verb in ACTION_VERBS:
        n = len(re.findall(rf"\b{verb}\b", lower))
        if n:
            counts[verb] = n
    return counts


def find_weak_phrases(text):
    lower = text.lower()
    return [phrase for phrase in WEAK_PHRASES if phrase in lower]


def word_count(text):
    return len(re.findall(r"\b\w+\b", text))


def top_keywords(text, n=15):
    tokens = tokenize(text)
    freq = Counter(tokens)
    return freq.most_common(n)
