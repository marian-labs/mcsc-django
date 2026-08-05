from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError

class SupabaseS3Storage(S3Boto3Storage):
    """
    Custom S3Boto3Storage for Supabase S3 API compatibility.
    Supabase S3 storage endpoint returns 403 Forbidden instead of 404 Not Found
    for head_object/delete_object checks when objects do not exist or when accessed via API.
    """
    def exists(self, name):
        try:
            return super().exists(name)
        except ClientError as err:
            status_code = err.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status_code in (403, 404):
                return False
            raise

    def delete(self, name):
        try:
            super().delete(name)
        except ClientError as err:
            status_code = err.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status_code in (403, 404):
                pass  # Ignore missing objects on remote bucket
            else:
                raise
