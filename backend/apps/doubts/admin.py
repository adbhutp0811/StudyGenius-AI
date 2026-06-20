from django.contrib import admin
from .models import ChatSession, ChatMessage, BookmarkedAnswer

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'subject', 'is_active', 'created_at')
    list_filter = ('subject', 'is_active')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'is_bookmarked', 'created_at')
    list_filter = ('role', 'is_bookmarked')

@admin.register(BookmarkedAnswer)
class BookmarkedAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
