# Resume Analyzer — AI/ML & NLP Powered Resume Scoring Platform

A full-stack web application that analyzes resumes using Natural Language
Processing and Machine Learning, giving job seekers an instant ATS-style
score, section-by-section feedback, extracted skills, and an optional
keyword-match score against a target job description.

Built with **Django** (backend + templating), vanilla **HTML/CSS/JS**
(frontend), and **scikit-learn / NLTK** (NLP & ML). Designed as a
final-year AI & ML portfolio project — every analysis runs **fully
offline**, with no external AI API calls, so it's easy to demo and
easy to explain in a viva/interview.

---

## ✨ Features

- **Drag-and-drop resume upload** — PDF, DOCX, or TXT (max 5MB)
- **ATS-style score (0–100)** with a transparent, weighted breakdown:
  section completeness, contact info, skills coverage, action-verb/impact
  language, resume length, and generic-phrase penalties
- **Skill extraction** across 7 categories (100+ keywords): programming
  languages, web dev, data science/ML, databases, cloud/DevOps, soft
  skills, tools & platforms
- **Section detection** — flags whether Summary, Education, Experience,
  Skills, Projects, Certifications, Achievements are present
- **Contact info extraction** — email, phone, LinkedIn, GitHub via regex
- **Education & experience parsing** — degree keywords and an estimated
  years-of-experience figure from date ranges
- **Job description matching** — TF-IDF vectorization + cosine similarity
  between resume and a pasted JD, plus a ranked list of missing JD
  keywords
- **Actionable suggestions** — a rule-based feedback engine tells the
  user exactly what to fix
- **History page** — every analysis is persisted (SQLite) and browsable
- **JSON API** (`/api/analyze/`) for programmatic access
- **Responsive, distinctive UI** — a paper/ink/highlighter "desk review"
  visual theme (not a generic Bootstrap template)

---

## 🧠 How the ML/NLP pipeline works

```
Upload (PDF/DOCX/TXT)
   │
   ▼
text_extractor.py   → pdfplumber / python-docx text extraction
   │
   ▼
nlp_processor.py    → cleaning, tokenization (NLTK), regex-based entity
                       extraction (email/phone/links), section detection,
                       skill/degree keyword matching, action-verb & weak-
                       phrase detection
   │
   ▼
scorer.py           → weighted rule-based ATS score (0-100)
                     → TF-IDF (scikit-learn) + cosine similarity for
                       resume ↔ job-description match
                     → rule-based suggestion generator
   │
   ▼
Django view saves a ResumeAnalysis row (SQLite, report stored as JSON)
   │
   ▼
Result page renders the score gauge, breakdown bars, skill chips, etc.
```

This project deliberately favors **transparent, explainable NLP**
(TF-IDF, regex, keyword dictionaries) over opaque deep-learning models —
it's easier to defend in a viva ("why did my resume get 72?") and it
runs on any laptop with no GPU and no model downloads. The `analyzer/ml/`
package is intentionally decoupled from Django, so the entire scoring
engine can be unit-tested or reused outside the web app.

---

## 📁 Project structure

```
resume_analyzer/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── sample_resumes/            # sample PDF/DOCX/TXT resumes for quick testing
│
├── resume_analyzer/           # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py / asgi.py
│
├── analyzer/                  # Main Django app
│   ├── models.py              # ResumeAnalysis model
│   ├── forms.py                # Upload form + validation
│   ├── views.py                # home / analyze / result / history / API
│   ├── urls.py
│   ├── admin.py
│   │
│   ├── ml/                    # Framework-agnostic ML/NLP engine
│   │   ├── skills_data.py     # skills / sections / degree keyword dictionaries
│   │   ├── text_extractor.py  # PDF/DOCX/TXT → plain text
│   │   ├── nlp_processor.py   # cleaning, tokenizing, entity extraction
│   │   └── scorer.py          # ATS scoring + TF-IDF JD matching
│   │
│   ├── templates/analyzer/
│   │   ├── base.html
│   │   ├── home.html          # upload page
│   │   ├── result.html        # analysis report page
│   │   └── history.html
│   │
│   └── static/analyzer/
│       ├── css/style.css      # full visual design system
│       └── js/script.js       # dropzone + form UX
│
└── media/resumes/             # uploaded resume files (gitignored)
```

---

## 🚀 Getting started

### 1. Clone / unzip and create a virtual environment

```bash
cd resume_analyzer
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. (Optional) Create an admin account

```bash
python manage.py createsuperuser
```

### 5. Run the development server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** and upload one of the files in
`sample_resumes/` to see it in action.

> **First run note:** the app tries to use NLTK's `punkt` tokenizer and
> stopword list. If they aren't already cached on your machine, it will
> attempt a one-time download. If you're offline, the app automatically
> falls back to a regex-based tokenizer — analysis still works, just
> with slightly simpler tokenization.

---

## 🔌 API usage

```bash
curl -X POST http://127.0.0.1:8000/api/analyze/ \
  -F "resume_file=@sample_resumes/sample_resume.pdf" \
  -F "job_description=Looking for a Python/Django developer with AWS experience"
```

Returns a JSON report identical to what powers the result page (ATS
score, breakdown, skills, sections, JD match, suggestions).

---

## 🛠️ Tech stack

| Layer          | Technology                                  |
|----------------|----------------------------------------------|
| Backend        | Django 4.2+ (views, ORM, forms, admin)       |
| ML / NLP       | scikit-learn (TF-IDF, cosine similarity), NLTK (tokenization, stopwords) |
| File parsing   | pdfplumber (PDF), python-docx (DOCX)         |
| Database       | SQLite (swap `DATABASES` in settings.py for Postgres/MySQL in production) |
| Frontend       | Server-rendered Django templates + vanilla CSS/JS (no build step) |

---

## 📈 Possible extensions (great "future work" talking points)

- Swap the rule-based scorer for a trained classifier (e.g. logistic
  regression on labeled "good/bad" resumes) while keeping the current
  engine as an explainable baseline
- Add spaCy-based Named Entity Recognition for company/job-title
  extraction
- Support DOC (legacy Word) and image-based/scanned PDFs via OCR
  (pytesseract)
- User accounts so people can track resume score improvements over time
- Resume rewriting suggestions using a generative model
- Export the analysis report as a downloadable PDF

---

## ⚠️ Notes

- This is an educational/portfolio tool. The ATS score is a heuristic
  approximation of how real applicant-tracking systems evaluate
  resumes — it is not affiliated with or identical to any commercial
  ATS product.
- Change `SECRET_KEY` in `settings.py` and set `DEBUG = False` with a
  proper `ALLOWED_HOSTS` before any real deployment.
