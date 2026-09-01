import io

try:
    import boto3
    from botocore.exceptions import BotoCoreError, NoCredentialsError
    _boto_available = True
except ImportError:
    _boto_available = False


def upload_to_s3(data: bytes, bucket: str, key: str) -> bool:
    if not _boto_available or not bucket:
        return False
    try:
        client = boto3.client("s3")
        client.upload_fileobj(io.BytesIO(data), bucket, key)
        return True
    except (BotoCoreError, NoCredentialsError, Exception):
        return False
