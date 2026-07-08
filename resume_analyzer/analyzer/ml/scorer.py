"""
Scoring engine: combines rule-based heuristics with a scikit-learn
TF-IDF + cosine-similarity model to score resumes and, optionally,
match them against a target job description.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from . import nlp_processor as nlp
from .skills_data import SECTION_SYNONYMS

# Section weights for the overall completeness score
SECTION_WEIGHTS = {
    "contact": 10,
    "summary": 5,
    "education": 15,
    "experience": 20,
    "skills": 20,
    "projects": 15,
    "certifications": 8,
    "achievements": 7,
}


def _grade(score):
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Average"
    return "Needs Improvement"


def compute_ats_score(text, sections, contact_info, skills_found, action_verb_count,
                       weak_phrases, wc):
    """Rule-based ATS-style score out of 100, with a transparent breakdown."""
    breakdown = {}

    # 1. Section completeness (max 45)
    section_score = 0
    for section, present in sections.items():
        if present:
            section_score += SECTION_WEIGHTS.get(section, 5)
    section_score = min(45, round(section_score * 45 / 100))
    breakdown["Section Completeness"] = {"score": section_score, "max": 45}

    # 2. Contact info completeness (max 10)
    contact_score = sum(
        2.5 for v in [contact_info["email"], contact_info["phone"],
                      contact_info["linkedin"], contact_info["github"]] if v
    )
    breakdown["Contact Information"] = {"score": round(contact_score), "max": 10}

    # 3. Skills richness (max 20) — scaled, cap at 15 distinct skills
    skills_score = min(20, round(len(skills_found) / 15 * 20))
    breakdown["Skills Coverage"] = {"score": skills_score, "max": 20}

    # 4. Action-verb usage / impact language (max 15)
    verb_score = min(15, round(sum(action_verb_count.values()) / 10 * 15))
    breakdown["Impact Language (Action Verbs)"] = {"score": verb_score, "max": 15}

    # 5. Length appropriateness (max 5) — ideal 350-900 words
    if 350 <= wc <= 900:
        length_score = 5
    elif 200 <= wc < 350 or 900 < wc <= 1200:
        length_score = 3
    else:
        length_score = 1
    breakdown["Resume Length"] = {"score": length_score, "max": 5}

    # 6. Penalty for weak/generic phrases (max 5, lose points per phrase)
    phrase_score = max(0, 5 - len(weak_phrases) * 1.5)
    breakdown["Language Quality"] = {"score": round(phrase_score), "max": 5}

    total = sum(v["score"] for v in breakdown.values())
    total = max(0, min(100, round(total)))

    return total, breakdown


def match_job_description(resume_text, jd_text):
    """TF-IDF + cosine similarity match score (0-100) between resume and JD,
    plus the JD keywords missing from the resume."""
    documents = [resume_text, jd_text]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    match_percent = round(float(similarity) * 100, 1)

    # Identify important JD keywords absent from the resume
    jd_tokens = set(nlp.tokenize(jd_text))
    resume_tokens = set(nlp.tokenize(resume_text))
    missing = sorted(jd_tokens - resume_tokens)

    # Rank missing keywords by TF-IDF weight in the JD so the most
    # important missing terms surface first.
    feature_names = vectorizer.get_feature_names_out()
    jd_vector = tfidf_matrix[1].toarray()[0]
    weights = dict(zip(feature_names, jd_vector))
    missing_ranked = sorted(
        [w for w in missing if w in weights],
        key=lambda w: weights[w],
        reverse=True,
    )[:15]

    return match_percent, missing_ranked


def analyze_resume(resume_text, job_description=None):
    """Run the full analysis pipeline and return a structured report dict."""
    text = nlp.clean_text(resume_text)

    contact_info = nlp.extract_contact_info(text)
    sections = nlp.detect_sections(text)
    skills_found = nlp.extract_skills(text)
    education_found = nlp.extract_education(text)
    action_verbs = nlp.count_action_verbs(text)
    weak_phrases = nlp.find_weak_phrases(text)
    wc = nlp.word_count(text)
    keywords = nlp.top_keywords(text, n=15)
    experience_years = nlp.estimate_experience_years(text)

    ats_score, breakdown = compute_ats_score(
        text, sections, contact_info, skills_found, action_verbs, weak_phrases, wc
    )

    # Suggestions engine — simple rule-based feedback generator
    suggestions = []
    if not contact_info["email"]:
        suggestions.append("Add a professional email address near the top of your resume.")
    if not contact_info["phone"]:
        suggestions.append("Include a phone number so recruiters can reach you.")
    if not contact_info["linkedin"]:
        suggestions.append("Add your LinkedIn profile URL.")
    if not sections.get("summary"):
        suggestions.append("Add a short professional summary/objective at the top.")
    if not sections.get("projects"):
        suggestions.append("Add a Projects section — concrete projects strongly boost credibility.")
    if not sections.get("certifications"):
        suggestions.append("List relevant certifications or online courses, if any.")
    if len(skills_found) < 8:
        suggestions.append("List more relevant technical and soft skills explicitly in a Skills section.")
    if sum(action_verbs.values()) < 5:
        suggestions.append("Use more strong action verbs (e.g., 'developed', 'led', 'optimized') to describe achievements.")
    if weak_phrases:
        suggestions.append(f"Replace generic phrases like {', '.join(weak_phrases[:3])} with measurable achievements.")
    if wc < 250:
        suggestions.append("Your resume looks short — add more detail about your experience and projects.")
    elif wc > 1200:
        suggestions.append("Your resume is quite long — consider trimming it to 1-2 pages.")
    if not suggestions:
        suggestions.append("Great job! Your resume covers the key sections well. Fine-tune wording for extra polish.")

    report = {
        "word_count": wc,
        "ats_score": ats_score,
        "ats_grade": _grade(ats_score),
        "score_breakdown": breakdown,
        "contact_info": contact_info,
        "sections_found": sections,
        "skills_found": skills_found,
        "education_found": education_found,
        "action_verbs_used": dict(action_verbs),
        "weak_phrases": weak_phrases,
        "top_keywords": keywords,
        "estimated_experience_years": experience_years,
        "suggestions": suggestions,
    }

    if job_description and job_description.strip():
        match_percent, missing_keywords = match_job_description(text, job_description)
        report["jd_match_percent"] = match_percent
        report["jd_missing_keywords"] = missing_keywords
        report["jd_grade"] = _grade(match_percent)

    return report
