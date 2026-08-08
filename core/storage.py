from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError, BotoCoreError
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Cache signed URLs for 90% of their expiry time so cached URLs are always valid.
# AWS_QUERYSTRING_EXPIRE controls how long Supabase signed URLs remain valid (default 3600s).
_URL_EXPIRY = getattr(settings, 'AWS_QUERYSTRING_EXPIRE', 3600)
_URL_CACHE_TTL = int(_URL_EXPIRY * 0.9)  # e.g. 3240s when expiry is 3600s


class SupabaseS3Storage(S3Boto3Storage):
    """
    Custom S3Boto3Storage for Supabase S3 API compatibility.
    Caches generated signed URLs for 90% of their signed expiry window so that
    the cached URL is always valid when returned (never returns an already-expired URL).
    """
    def url(self, name, parameters=None, expire=None, http_method=None):
        if not name:
            return ""
        clean_name = str(name).replace('\\', '/')
        cache_key = f"supabase_url:{clean_name}"
        cached_url = cache.get(cache_key)
        if cached_url:
            return cached_url

        url = super().url(clean_name, parameters=parameters, expire=expire, http_method=http_method)
        # Cache for 90% of the signed URL's lifetime so it's refreshed before it expires
        cache.set(cache_key, url, _URL_CACHE_TTL)
        return url

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
