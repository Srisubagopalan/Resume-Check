"""
Unit tests for the resume analyzer.

Run with: python manage.py test
"""
import io
import os

from django.test import TestCase, Client
from django.urls import reverse

from analyzer.ml import nlp_processor as nlp
from analyzer.ml.scorer import analyze_resume, match_job_description
from analyzer.ml.skills_data import ALL_SKILLS

SAMPLE_RESUME = """
Jane Doe
jane.doe@email.com | +1-202-555-0100
linkedin.com/in/janedoe | github.com/janedoe

Summary
Final year Computer Science student focused on machine learning and backend development.

Education
B.Tech in Computer Science, ABC University, 2020-2024

Experience
Backend Developer Intern, DataCorp, 2023-2024
Developed REST APIs using Django and PostgreSQL. Implemented a machine learning
pipeline with scikit-learn. Collaborated with a cross-functional team using Git.

Projects
Resume Analyzer: built an NLP based scoring tool with Python, NLTK, and Django.

Skills
Python, Django, SQL, Machine Learning, Git, Docker

Certifications
AWS Certified Cloud Practitioner
"""

JOB_DESCRIPTION = """
We are hiring a Python/Django backend developer with experience in AWS,
Docker, Kubernetes, and strong communication skills.
"""


class NLPProcessorTests(TestCase):
    def test_extract_contact_info_finds_all_fields(self):
        info = nlp.extract_contact_info(SAMPLE_RESUME)
        self.assertEqual(info["email"], "jane.doe@email.com")
        self.assertIsNotNone(info["phone"])
        self.assertIn("linkedin.com/in/janedoe", info["linkedin"])
        self.assertIn("github.com/janedoe", info["github"])

    def test_detect_sections(self):
        sections = nlp.detect_sections(SAMPLE_RESUME)
        for name in ("summary", "education", "experience", "skills",
                      "projects", "certifications"):
            self.assertTrue(sections[name], f"expected section '{name}' to be detected")

    def test_extract_skills_matches_known_skills(self):
        skills = nlp.extract_skills(SAMPLE_RESUME)
        self.assertIn("python", skills)
        self.assertIn("django", skills)
        self.assertIn("machine learning", skills)
        # every returned skill must come from the canonical skill list
        self.assertTrue(set(skills).issubset(set(ALL_SKILLS)))

    def test_extract_education_no_false_positive_from_urls(self):
        # regression test: "github.com" must not match the "b.com" degree keyword
        education = nlp.extract_education("Find me at github.com/janedoe")
        self.assertNotIn("b.com", education)

    def test_extract_education_matches_real_degree(self):
        education = nlp.extract_education(SAMPLE_RESUME)
        self.assertIn("b.tech", education)

    def test_word_count_reasonable(self):
        wc = nlp.word_count(SAMPLE_RESUME)
        self.assertGreater(wc, 30)


class ScorerTests(TestCase):
    def test_analyze_resume_returns_expected_keys(self):
        report = analyze_resume(SAMPLE_RESUME)
        for key in ("ats_score", "ats_grade", "score_breakdown", "contact_info",
                    "sections_found", "skills_found", "suggestions"):
            self.assertIn(key, report)
        self.assertGreaterEqual(report["ats_score"], 0)
        self.assertLessEqual(report["ats_score"], 100)

    def test_analyze_resume_with_job_description_adds_match_fields(self):
        report = analyze_resume(SAMPLE_RESUME, JOB_DESCRIPTION)
        self.assertIn("jd_match_percent", report)
        self.assertIn("jd_missing_keywords", report)
        self.assertGreaterEqual(report["jd_match_percent"], 0)
        self.assertLessEqual(report["jd_match_percent"], 100)

    def test_match_job_description_identifies_missing_keywords(self):
        _, missing = match_job_description(SAMPLE_RESUME, JOB_DESCRIPTION)
        # "kubernetes" is in the JD but not the resume
        self.assertIn("kubernetes", missing)

    def test_empty_resume_scores_low(self):
        report = analyze_resume("Hello world.")
        self.assertLess(report["ats_score"], 40)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get(reverse("analyzer:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analyze Resume")

    def test_analyze_rejects_bad_file_type(self):
        bad_file = io.BytesIO(b"not a real resume")
        bad_file.name = "resume.exe"
        response = self.client.post(reverse("analyzer:analyze"), {"resume_file": bad_file})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("analyzer:home"))

    def test_analyze_txt_resume_end_to_end(self):
        txt_file = io.BytesIO(SAMPLE_RESUME.encode("utf-8"))
        txt_file.name = "resume.txt"
        response = self.client.post(
            reverse("analyzer:analyze"),
            {"resume_file": txt_file, "job_description": JOB_DESCRIPTION},
        )
        self.assertEqual(response.status_code, 302)

        result_response = self.client.get(response["Location"])
        self.assertEqual(result_response.status_code, 200)
        self.assertContains(result_response, "gauge-score")

    def test_history_page_loads(self):
        response = self.client.get(reverse("analyzer:history"))
        self.assertEqual(response.status_code, 200)

    def test_api_analyze_returns_json_report(self):
        txt_file = io.BytesIO(SAMPLE_RESUME.encode("utf-8"))
        txt_file.name = "resume.txt"
        response = self.client.post(reverse("analyzer:analyze_api"), {"resume_file": txt_file})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("ats_score", data["report"])
