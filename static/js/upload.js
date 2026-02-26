document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("uploadForm");
  if (!form) return; // not on upload page

  const fileInput = document.getElementById("file");
  const statusEl = document.getElementById("uploadStatus");
  const keyEl = document.getElementById("uploadKey");
  const btn = document.getElementById("uploadBtn");

  if (!fileInput || !statusEl || !keyEl || !btn) {
    console.error("Upload page elements not found");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const file = fileInput.files[0];
    if (!file) {
      statusEl.textContent = "Please select a file.";
      keyEl.textContent = "";
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    btn.disabled = true;
    statusEl.textContent = "Uploading...";
    keyEl.textContent = "";

    try {
      const res = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        statusEl.textContent = data.error || "Upload failed";
        keyEl.textContent = data.details ? String(data.details) : "";
        return;
      }

      statusEl.textContent = "Upload successful!";
      keyEl.textContent = `S3 key: ${data.s3_key}`;
      fileInput.value = "";
    } catch (err) {
      statusEl.textContent = "Upload failed";
      keyEl.textContent = err.message || String(err);
    } finally {
      btn.disabled = false;
    }
  });
});
