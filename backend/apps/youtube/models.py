from django.db import models
from django.conf import settings
import uuid

class VideoSummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_summaries')
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=2000)
    video_id = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=255, blank=True)
    duration = models.IntegerField(default=0)
    thumbnail_url = models.URLField(max_length=2000, blank=True)
    transcript = models.TextField(blank=True)
    summary = models.TextField()
    key_points = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    quiz = models.JSONField(default=list, blank=True)
    language = models.CharField(max_length=10, default='en')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'video_summaries'
        ordering = ['-created_at']

    def __str__(self):
        return self.title[:50]


class SavedNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video_summary = models.ForeignKey(VideoSummary, on_delete=models.CASCADE, related_name='saved_notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'video_saved_notes'
