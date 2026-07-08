from django.db import models
from django.contrib.auth.models import User


def resume_upload_path(instance, filename):
    return f"resumes/{filename}"


class ResumeAnalysis(models.Model):
    """Stores an uploaded resume and the resulting analysis report."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                              related_name="analyses")
    resume_file = models.FileField(upload_to=resume_upload_path)
    original_filename = models.CharField(max_length=300)
    job_description = models.TextField(blank=True, null=True)

    extracted_text = models.TextField(blank=True)
    ats_score = models.FloatField(default=0)
    ats_grade = models.CharField(max_length=50, blank=True)
    jd_match_percent = models.FloatField(null=True, blank=True)

    report_json = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Resume Analyses"

    def __str__(self):
        return f"{self.original_filename} ({self.ats_score:.0f}%) - {self.created_at:%Y-%m-%d %H:%M}"
