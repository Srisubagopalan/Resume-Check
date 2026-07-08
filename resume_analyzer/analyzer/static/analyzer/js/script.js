// Resume Analyzer — small progressive-enhancement script
// Handles drag-and-drop file feedback and a loading state on submit.
// No frameworks; degrades gracefully if JS is disabled (plain form still works).

document.addEventListener("DOMContentLoaded", function () {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("id_resume_file");
  const fileNameEl = document.getElementById("file-name");
  const form = document.getElementById("analyze-form");
  const submitBtn = document.getElementById("submit-btn");

  if (!dropzone || !fileInput) return;

  function showFileName(file) {
    if (!file) return;
    const sizeKb = Math.round(file.size / 1024);
    fileNameEl.textContent = `${file.name} (${sizeKb} KB)`;
  }

  fileInput.addEventListener("change", function () {
    if (fileInput.files && fileInput.files[0]) {
      showFileName(fileInput.files[0]);
    }
  });

  ["dragenter", "dragover"].forEach((evt) => {
    dropzone.addEventListener(evt, function (e) {
      e.preventDefault();
      dropzone.classList.add("is-dragover");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropzone.addEventListener(evt, function (e) {
      e.preventDefault();
      dropzone.classList.remove("is-dragover");
    });
  });

  dropzone.addEventListener("drop", function (e) {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length) {
      fileInput.files = dt.files;
      showFileName(dt.files[0]);
    }
  });

  if (form && submitBtn) {
    form.addEventListener("submit", function () {
      if (!fileInput.files || !fileInput.files[0]) return;
      submitBtn.classList.add("is-loading");
      submitBtn.querySelector(".btn-label").textContent = "Analyzing...";
      submitBtn.disabled = true;
    });
  }
});
