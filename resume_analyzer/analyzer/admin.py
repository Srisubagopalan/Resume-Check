from django.contrib import admin
from .models import ResumeAnalysis


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "ats_score", "ats_grade", "jd_match_percent", "created_at")
    list_filter = ("ats_grade", "created_at")
    search_fields = ("original_filename",)
    readonly_fields = ("extracted_text", "report_json", "created_at")
