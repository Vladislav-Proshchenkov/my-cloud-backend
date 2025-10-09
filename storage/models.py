import uuid
import os
from django.db import models
from django.conf import settings


def user_directory_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"user_{instance.user.id}/{filename}" # Файлы будут сохраняться в MEDIA_ROOT/user_<id>/<uuid>_<filename>


class UserFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    size = models.BigIntegerField(default=0)
    upload_date = models.DateTimeField(auto_now_add=True)
    last_download = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    unique_identifier = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.original_name} ({self.user.username})"

    def save(self, *args, **kwargs):
        if not self.size and self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)
