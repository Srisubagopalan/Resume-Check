from django import forms

ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]
MAX_FILE_SIZE_MB = 5


class ResumeUploadForm(forms.Form):
    resume_file = forms.FileField(
        label="Upload your resume",
        widget=forms.ClearableFileInput(attrs={
            "accept": ".pdf,.docx,.txt",
            "class": "file-input",
        }),
    )
    job_description = forms.CharField(
        label="Target job description ",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 6,
            "placeholder": "Paste a job description here to get a match score "
                           "against this specific role ...",
            "class": "textarea-input",
        }),
    )

    def clean_resume_file(self):
        f = self.cleaned_data["resume_file"]
        name = f.name.lower()

        if not any(name.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise forms.ValidationError(
                "Unsupported file type. Please upload a PDF, DOCX, or TXT file."
            )

        if f.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise forms.ValidationError(
                f"File too large. Please upload a file under {MAX_FILE_SIZE_MB}MB."
            )

        return f
