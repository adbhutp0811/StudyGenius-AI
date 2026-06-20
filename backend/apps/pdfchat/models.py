from django.db import models
from django.conf import settings
import uuid

class PDFDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pdf_documents')
    file = models.FileField(upload_to='pdfs/')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    file_size = models.IntegerField(default=0)
    page_count = models.IntegerField(default=0)
    content_text = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pdf_documents'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PDFChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pdf_chat_sessions')
    pdf_documents = models.ManyToManyField(PDFDocument, related_name='chat_sessions')
    title = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pdf_chat_sessions'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title


class PDFChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(PDFChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    relevant_sections = models.JSONField(default=list, blank=True)
    page_references = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pdf_chat_messages'
        ordering = ['created_at']


class DocumentHighlight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='highlights')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pdf_highlights')
    text = models.TextField()
    page_number = models.IntegerField(default=0)
    color = models.CharField(max_length=20, default='yellow')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_highlights'
