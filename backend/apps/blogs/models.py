from django.db import models
from django.conf import settings
import uuid

class Blog(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=500)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    keywords = models.JSONField(default=list, blank=True)
    seo_title = models.CharField(max_length=500, blank=True)
    seo_description = models.TextField(blank=True)
    seo_tags = models.JSONField(default=list, blank=True)
    cover_image = models.ImageField(upload_to='blog_covers/', blank=True, null=True)
    reading_time = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_generated = models.BooleanField(default=False)
    grammar_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'blogs'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class BlogVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=500)
    content = models.TextField()
    version_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blog_versions'
        ordering = ['-version_number']


class SEOSuggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='seo_suggestions')
    suggestion_type = models.CharField(max_length=50)
    current_value = models.TextField(blank=True)
    suggested_value = models.TextField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'seo_suggestions'
