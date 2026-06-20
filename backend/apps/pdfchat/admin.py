from django.contrib import admin
from .models import PDFDocument, PDFChatSession, PDFChatMessage, DocumentHighlight

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'page_count', 'is_processed', 'created_at')
    list_filter = ('is_processed',)
    search_fields = ('title', 'user__email')

@admin.register(PDFChatSession)
class PDFChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'created_at')

@admin.register(PDFChatMessage)
class PDFChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'created_at')
    list_filter = ('role',)

@admin.register(DocumentHighlight)
class DocumentHighlightAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'page_number', 'color')
