from config import S3_BUCKET, S3_PREFIX, ALLOWED_EXTENSIONS
import boto3
from datetime import datetime, timezone



s3 = boto3.client("s3")


def allowed_file(filename: str) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def sanitize_filename(name: str) -> str:
    """
    Minimal filename sanitization:
    - keeps letters, digits, dot, dash, underscore
    - replaces spaces with underscore
    """
    name = (name or "").strip().replace(" ", "_")
    return "".join(ch for ch in name if ch.isalnum() or ch in {".", "-", "_"})




def upload_file_to_s3(file) -> str:
    """
    Uploads a file object (Flask FileStorage) to S3.
    Returns the S3 key.
    """
    original = (file.filename or "").strip()
    if not original:
        raise ValueError("Empty filename")

    if not allowed_file(original):
        raise ValueError("Only PDF and TXT files are allowed")

    safe_name = sanitize_filename(original)
    if not safe_name:
        raise ValueError("Invalid filename")

    # timestamp to avoid filename collisions
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    s3_key = f"{S3_PREFIX}{ts}_{safe_name}"

    s3.upload_fileobj(file, S3_BUCKET, s3_key)
    return s3_key