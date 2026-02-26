import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
KNOWLEDGE_BASE_ID = os.getenv("KNOWLEDGE_BASE_ID")
DATA_SOURCE_ID = os.getenv("DATA_SOURCE_ID")
MODEL_ID = os.getenv("MODEL_ID")
APP_PORT = int(os.getenv("APP_PORT", 5000))
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_DEBUG = os.getenv("APP_DEBUG", "FALSE").lower() == "true"

S3_BUCKET = os.getenv("S3_BUCKET")
S3_PREFIX = os.getenv("S3_PREFIX")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10 )) * 1024 * 1024 # Default to 10 MB 
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "pdf,txt").split(","))

# print(f"Configuration loaded: APP_HOST={APP_HOST}, APP_PORT={APP_PORT}, S3_BUCKET={S3_BUCKET}, S3_PREFIX={S3_PREFIX}, ALLOWED_EXTENSIONS={ALLOWED_EXTENSIONS}, MAX_FILE_SIZE_MB={MAX_FILE_SIZE_MB}")