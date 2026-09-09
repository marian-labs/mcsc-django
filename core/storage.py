from django.core.files.storage import FileSystemStorage
import logging

logger = logging.getLogger(__name__)


class OverwriteFileSystemStorage(FileSystemStorage):
    """
    Custom FileSystemStorage for VPS disk media storage.
    Automatically handles existing files and ensures reliable file access.
    """
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return super().get_available_name(name, max_length=max_length)

