import boto3
from typing import Any, Dict, List, Optional
from config import AWS_REGION, KNOWLEDGE_BASE_ID, MODEL_ID, DATA_SOURCE_ID

bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=AWS_REGION)
bedrock_agent_mgmt = boto3.client("bedrock-agent", region_name=AWS_REGION)


def start_kb_sync() -> str:
    """
    Starts a KB ingestion job (sync) for the configured data source.
    Returns ingestionJobId.
    """
    if not DATA_SOURCE_ID:
        raise ValueError("DATA_SOURCE_ID is missing (set it in .env)")

    resp = bedrock_agent_mgmt.start_ingestion_job(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        dataSourceId=DATA_SOURCE_ID,
        description="Sync after S3 upload"  
    )
    return resp["ingestionJob"]["ingestionJobId"]

def _extract_sources(resp: Dict[str, Any], max_items: int = 5) -> List[Dict[str, str]]:
    """
    Best-effort extraction of retrieved context from Bedrock retrieve_and_generate response.
    Returns a list of dicts: { "text": "...", "source": "..." }
    If the structure doesn't match, returns [].
    """
    sources: List[Dict[str, str]] = []

    # Common pattern: resp["citations"] -> list of citation objects
    citations = resp.get("citations")
    if isinstance(citations, list):
        for c in citations:
            if not isinstance(c, dict):
                continue

            retrieved = c.get("retrievedReferences") or c.get("retrievedReference") or c.get("references")
            if isinstance(retrieved, list):
                for r in retrieved:
                    if not isinstance(r, dict):
                        continue

                    # Text can appear under different keys depending on API version
                    text = (
                        (r.get("content") or {}).get("text")
                        if isinstance(r.get("content"), dict)
                        else r.get("text") or r.get("content") or ""
                    )

                    # Source/location keys vary
                    location = r.get("location") or {}
                    source = ""
                    if isinstance(location, dict):
                        # S3 location is common
                        s3 = location.get("s3Location") or location.get("s3_location") or {}
                        if isinstance(s3, dict):
                            bucket = s3.get("bucket") or ""
                            key = s3.get("key") or ""
                            if bucket or key:
                                source = f"s3://{bucket}/{key}".strip("/")
                        # Some responses provide a uri/url directly
                        source = source or location.get("uri") or location.get("url") or ""

                    if isinstance(text, str) and text.strip():
                        sources.append({
                            "text": text.strip(),
                            "source": str(source) if source else ""
                        })

                    if len(sources) >= max_items:
                        return sources

    # Fallback: some variants include retrieved text elsewhere
    # (we keep it conservative to avoid breaking)
    return sources


def query_knowledge_base(question: str, include_sources: bool = True) -> Dict[str, Any]:
    response = bedrock_agent.retrieve_and_generate(
        input={"text": question},
        retrieveAndGenerateConfiguration={
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": {
                "knowledgeBaseId": KNOWLEDGE_BASE_ID,
                "modelArn": f"arn:aws:bedrock:{AWS_REGION}::foundation-model/{MODEL_ID}",
            },
        },
    )

    answer = (response.get("output") or {}).get("text") or ""
    sources = _extract_sources(response) if include_sources else []

    return {
        "answer": answer,
        "sources": sources,
    }
