from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError, BotoCoreError
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
_URL_CACHE_TTL = 86400


import urllib.parse


class SupabaseS3Storage(S3Boto3Storage):
    """
    Custom S3Boto3Storage for Supabase Storage.
    Generates clean, permanent, public URLs without presigned query parameters.
    Allows browsers, CDNs, and first-time visitors to load images reliably and cache them permanently.
    """
    def url(self, name, parameters=None, expire=None, http_method=None):
        if not name:
            return ""
        clean_name = str(name).replace('\\', '/')
        supabase_url = getattr(settings, 'SUPABASE_URL', '')
        bucket_name = getattr(settings, 'SUPABASE_STORAGE_BUCKET_NAME', '')
        if supabase_url and bucket_name:
            qname = urllib.parse.quote(clean_name, safe='/')
            return f"{supabase_url}/storage/v1/object/public/{bucket_name}/{qname}"

        return super().url(clean_name, parameters=parameters, expire=expire, http_method=http_method)

    def exists(self, name):
        try:
            return super().exists(name)
        except (ClientError, BotoCoreError) as err:
            status_code = getattr(err, 'response', {}).get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status_code in (403, 404):
                return False
            return False

    def delete(self, name):
        if name:
            clean_name = str(name).replace('\\', '/')
            cache.delete(f"supabase_url:{clean_name}")
        try:
            super().delete(name)
        except (ClientError, BotoCoreError) as err:
            status_code = getattr(err, 'response', {}).get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status_code in (403, 404):
                pass  # Ignore missing objects on remote bucket
            else:
                logger.warning(f"Failed to delete object {name} from Supabase S3: {err}")

    def _save(self, name, content):
        if name:
            clean_name = str(name).replace('\\', '/')
            cache.delete(f"supabase_url:{clean_name}")
        try:
            return super()._save(name, content)
        except (ClientError, BotoCoreError) as err:
            logger.error(f"Supabase S3 upload failed for '{name}': {err}. Falling back to local storage.")
            local_storage = FileSystemStorage()
            return local_storage.save(name, content)
