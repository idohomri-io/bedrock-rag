# Bedrock RAG — Document Q&A with Amazon Bedrock

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)
![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonaws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)

A general-purpose Retrieval-Augmented Generation (RAG) web application. Upload any PDF or TXT documents, then ask questions grounded strictly in their content. Built with Amazon Bedrock Knowledge Bases, Flask, and deployed on AWS EC2 via Docker.

---

## Overview

Users upload PDF or TXT documents on any topic through a web interface. The files are stored in Amazon S3 and automatically ingested into an Amazon Bedrock Knowledge Base — which handles chunking, embedding, and vector indexing. When a question is asked, Bedrock retrieves the most relevant context and generates a grounded answer using Claude, along with source citations.

```
Browser
  │
  ├── POST /upload ──► S3 Bucket ──► Bedrock Ingestion Job
  │                                        │
  │                                  Knowledge Base
  │
  └── POST /ask ─────────────────► Bedrock retrieve_and_generate
                                          │
                                    Answer + Citations
```

---

## Features

- Upload PDF and TXT documents through a web UI
- Answers are strictly grounded in uploaded documents — no hallucination beyond the knowledge base
- Source citations returned alongside each answer
- Knowledge Base sync triggered automatically after each upload
- Containerized with Docker, deployable to EC2 with IAM role-based auth

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask |
| AI / RAG | Amazon Bedrock, Bedrock Knowledge Bases |
| Storage | Amazon S3 |
| Frontend | HTML, CSS, Vanilla JS |
| Containerization | Docker, Gunicorn |
| AWS SDK | boto3 |

---

## Project Structure

```
bedrock-rag/
├── app.py              # Flask application — routes and request handling
├── config.py           # Environment variable loader
├── services/
│   ├── kb_client.py    # Bedrock Knowledge Base client (query + sync)
│   └── s3_client.py    # S3 upload with validation and sanitization
├── requirements.txt
├── Dockerfile
├── .env                # Not committed — see Environment Variables below
├── templates/
│   ├── base.html       # Shared layout and navigation
│   ├── index.html      # Chat / ask interface
│   └── upload.html     # Document upload interface
└── static/
    ├── css/main.css
    └── js/
        ├── main.js     # Chat UI logic and source rendering
        └── upload.js   # Upload form handler
```

---

## Local Setup

**Prerequisites:** Python 3.11+, AWS CLI configured with Bedrock and S3 access.

```bash
git clone https://github.com/idohomri-io/bedrock-rag.git
cd bedrock-rag

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # Fill in your values (see below)

python app.py
```

App runs at `http://localhost:5010` by default.

---

## Environment Variables

Create a `.env` file at the project root with the following:

| Variable | Description | Example |
|---|---|---|
| `AWS_REGION` | AWS region for all services | `us-east-1` |
| `KNOWLEDGE_BASE_ID` | Bedrock Knowledge Base ID | `PD4OESG4D3` |
| `DATA_SOURCE_ID` | Bedrock KB Data Source ID | `FWZF1K3FKM` |
| `MODEL_ID` | Bedrock model used for generation | `anthropic.claude-3-sonnet-20240229-v1:0` |
| `S3_BUCKET` | S3 bucket for document storage | `my-bedrock-docs` |
| `S3_PREFIX` | S3 key prefix for uploaded files | `data/` |
| `ALLOWED_EXTENSIONS` | Comma-separated allowed file types | `pdf,txt` |
| `MAX_FILE_SIZE_MB` | Max upload size in MB | `10` |
| `APP_PORT` | Port Flask listens on | `5010` |
| `APP_HOST` | Host Flask binds to | `0.0.0.0` |
| `DEBUG` | Flask debug mode | `True` |

AWS credentials are resolved via AWS CLI (`aws configure`) locally, or via an IAM Role when deployed on EC2.

---

## API Reference

| Method | Endpoint | Description | Request | Response |
|---|---|---|---|---|
| `GET` | `/` | Chat UI | — | HTML |
| `GET` | `/upload` | Upload UI | — | HTML |
| `GET` | `/health` | Health check | — | `{"status": "ok"}` |
| `POST` | `/ask` | Query the Knowledge Base | `{"question": "..."}` | `{"answer": "...", "sources": [...]}` |
| `POST` | `/upload` | Upload a document to S3 | `multipart/form-data` (field: `file`) | `{"message": "...", "s3_key": "...", "ingestion_job_id": "..."}` |

---

## Deployment (EC2 + Docker)

1. Provision an EC2 instance with an IAM Role that grants access to Amazon Bedrock and S3.
2. Install Docker on the instance.
3. Pull the image:
   ```bash
   docker pull idohomriio/network-rag-web
   ```
4. Create a `.env` file on the instance with your values, then run:
   ```bash
   docker run -d -p 5000:5000 --env-file .env idohomriio/network-rag-web
   ```

> AWS credentials inside the container are provided by the EC2 IAM Role automatically — no keys needed in the environment file. For local Docker runs, mount your `~/.aws` directory:
> ```bash
> docker run -d -p 5000:5000 --env-file .env -v ~/.aws:/root/.aws:ro idohomriio/network-rag-web
> ```

---

## How It Works

1. **Upload** — A document is uploaded via the web UI. The backend validates the file type and size, sanitizes the filename, and stores it in S3 under a timestamped key to prevent collisions.
2. **Ingestion** — After upload, the backend immediately triggers a Bedrock Knowledge Base ingestion job. Bedrock reads the new file from S3, chunks it, generates embeddings, and indexes them in the knowledge base.
3. **Query** — The user asks a question. The backend calls Bedrock's `retrieve_and_generate` API, which retrieves the most relevant document chunks and generates a grounded answer using Claude.
4. **Response** — The answer and source citations (including S3 locations) are returned and displayed in the UI.
