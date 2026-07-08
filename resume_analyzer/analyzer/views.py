import os
import uuid

from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .forms import ResumeUploadForm
from .models import ResumeAnalysis
from .ml.text_extractor import extract_text, TextExtractionError
from .ml.scorer import analyze_resume


def home(request):
    """Landing page with the upload form."""
    form = ResumeUploadForm()
    recent = ResumeAnalysis.objects.all()[:5]
    return render(request, "analyzer/home.html", {"form": form, "recent": recent})


@require_http_methods(["POST"])
def analyze(request):
    """Handle resume upload, run the ML/NLP pipeline, store + show results."""
    form = ResumeUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
        return redirect("analyzer:home")

    uploaded_file = form.cleaned_data["resume_file"]
    job_description = form.cleaned_data.get("job_description", "")

    # Save file with a unique name to avoid collisions
    ext = os.path.splitext(uploaded_file.name)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "resumes"))
    saved_name = fs.save(unique_name, uploaded_file)
    file_path = fs.path(saved_name)

    try:
        resume_text = extract_text(file_path)
        report = analyze_resume(resume_text, job_description)
    except TextExtractionError as exc:
        messages.error(request, str(exc))
        os.remove(file_path)
        return redirect("analyzer:home")
    except Exception as exc:
        messages.error(request, f"Something went wrong while analyzing your resume: {exc}")
        os.remove(file_path)
        return redirect("analyzer:home")

    analysis = ResumeAnalysis.objects.create(
        resume_file=f"resumes/{saved_name}",
        original_filename=uploaded_file.name,
        job_description=job_description,
        extracted_text=resume_text,
        ats_score=report["ats_score"],
        ats_grade=report["ats_grade"],
        jd_match_percent=report.get("jd_match_percent"),
        report_json=report,
    )

    return redirect("analyzer:result", pk=analysis.pk)


def result(request, pk):
    analysis = get_object_or_404(ResumeAnalysis, pk=pk)
    report = analysis.report_json
    return render(request, "analyzer/result.html", {"analysis": analysis, "report": report})


def history(request):
    analyses = ResumeAnalysis.objects.all()[:50]
    return render(request, "analyzer/history.html", {"analyses": analyses})


def analyze_api(request):
    """Simple JSON API endpoint for programmatic access (bonus feature)."""
    if request.method != "POST" or not request.FILES.get("resume_file"):
        return JsonResponse({"error": "POST a multipart form with 'resume_file'."}, status=400)

    uploaded_file = request.FILES["resume_file"]
    job_description = request.POST.get("job_description", "")

    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in (".pdf", ".docx", ".txt"):
        return JsonResponse({"error": "Unsupported file type."}, status=400)

    tmp_name = f"{uuid.uuid4().hex}{ext}"
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "resumes"))
    saved_name = fs.save(tmp_name, uploaded_file)
    file_path = fs.path(saved_name)

    try:
        resume_text = extract_text(file_path)
        report = analyze_resume(resume_text, job_description)
        return JsonResponse({"success": True, "report": report})
    except TextExtractionError as exc:
        return JsonResponse({"error": str(exc)}, status=422)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
