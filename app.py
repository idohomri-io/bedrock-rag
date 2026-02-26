from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from services.kb_client import query_knowledge_base, start_kb_sync
from services.s3_client import upload_file_to_s3
from config import APP_HOST, APP_PORT, APP_DEBUG, MAX_FILE_SIZE_MB


app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB 

# UI


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/upload")
def upload_page():
    return render_template("upload.html")


# API
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        result = query_knowledge_base(question)
        return jsonify(result)
    except Exception as e:
        # נוח לדיבוג בשלב הזה; בפרודקשן לא מחזירים str(e)
        return jsonify({"error": str(e)}), 500


@app.post("/upload")
def upload():
    """
    Accepts multipart/form-data with a 'file' field.
    Uploads only .pdf or .txt files to S3 under data/.
    """
    if "file" not in request.files:
        return jsonify({"error": "Missing 'file' field in form-data"}), 400

    file = request.files["file"]

    try:
        s3_key = upload_file_to_s3(file)
        
        # Trigger KB sync
        ingestion_job_id = start_kb_sync()

        return jsonify({
            "message": "File uploaded successfully",
            "s3_key": s3_key,
            "ingestion_job_id": ingestion_job_id
        }), 200

    except ValueError as ve:
        # validation issues (empty filename / invalid extension)
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        # unexpected / AWS errors
        return jsonify({"error": "Upload failed", "details": str(e)}), 500



# Error Handlers

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"error": "File too large. Max allowed size is 10MB."}), 413



# Run the app

if __name__ == "__main__":
    app.run(debug=APP_DEBUG, host=APP_HOST, port=APP_PORT)
