from django.contrib import admin
from .models import Blog, BlogVersion, SEOSuggestion

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'is_generated', 'word_count', 'created_at')
    list_filter = ('status', 'is_generated')
    search_fields = ('title', 'content', 'user__email')

@admin.register(BlogVersion)
class BlogVersionAdmin(admin.ModelAdmin):
    list_display = ('blog', 'version_number', 'created_at')

@admin.register(SEOSuggestion)
class SEOSuggestionAdmin(admin.ModelAdmin):
    list_display = ('blog', 'suggestion_type', 'created_at')
