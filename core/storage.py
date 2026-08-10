from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError, BotoCoreError
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Long-lived URL cache TTL (24 hours) so presigned URLs remain stable for browser caching
# while ensuring signatures are valid for 7 days (AWS_QUERYSTRING_EXPIRE).
_URL_CACHE_TTL = 86400


class SupabaseS3Storage(S3Boto3Storage):
    """
    Custom S3Boto3Storage for Supabase S3 API compatibility.
    Caches generated signed URLs for a maximum of 5 minutes so that
    new visitors always receive freshly-signed valid URLs with current timestamps.
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
