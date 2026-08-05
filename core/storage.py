from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError, BotoCoreError
from django.core.files.storage import FileSystemStorage
import logging

logger = logging.getLogger(__name__)

class SupabaseS3Storage(S3Boto3Storage):
    """
    Custom S3Boto3Storage for Supabase S3 API compatibility.
    Supabase S3 storage endpoint returns 403 Forbidden instead of 404 Not Found
    for head_object/delete_object checks when objects do not exist or when accessed via API.
    """
    def exists(self, name):
        try:
            return super().exists(name)
        except (ClientError, BotoCoreError) as err:
            status_code = getattr(err, 'response', {}).get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status_code in (403, 404):
                return False
            return False

    def delete(self, name):
        try:
            super().delete(name)
        except (ClientError, BotoCoreError) as err:
            status_code = getattr(err, 'response', {}).get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status_code in (403, 404):
                pass  # Ignore missing objects on remote bucket
            else:
                logger.warning(f"Failed to delete object {name} from Supabase S3: {err}")

    def _save(self, name, content):
        try:
            return super()._save(name, content)
        except (ClientError, BotoCoreError) as err:
            logger.error(f"Supabase S3 upload failed for '{name}': {err}. Falling back to local storage.")
            local_storage = FileSystemStorage()
            return local_storage.save(name, content)
