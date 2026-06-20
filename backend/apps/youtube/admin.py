from django.contrib import admin
from .models import VideoSummary, SavedNote

@admin.register(VideoSummary)
class VideoSummaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'channel_name', 'duration', 'created_at')
    search_fields = ('title', 'channel_name', 'user__email')

@admin.register(SavedNote)
class SavedNoteAdmin(admin.ModelAdmin):
    list_display = ('video_summary', 'created_at')
