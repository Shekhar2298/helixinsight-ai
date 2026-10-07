from __future__ import annotations
import io
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from .config import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )


def ensure_bucket() -> None:
    try:
        client = _client()
        existing = [b["Name"] for b in client.list_buckets().get("Buckets", [])]
        if settings.s3_bucket not in existing:
            client.create_bucket(Bucket=settings.s3_bucket)
    except (BotoCoreError, ClientError):
        return


def put_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str | None:
    try:
        ensure_bucket()
        _client().upload_fileobj(io.BytesIO(data), settings.s3_bucket, key, ExtraArgs={"ContentType": content_type})
        return f"s3://{settings.s3_bucket}/{key}"
    except (BotoCoreError, ClientError):
        return None
