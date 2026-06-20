from django.contrib import admin
from .models import Resume, ResumeTemplate, ResumeAnalysis

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'full_name', 'user', 'ats_score', 'is_complete', 'created_at')
    list_filter = ('is_complete',)
    search_fields = ('title', 'full_name', 'user__email')

@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_premium', 'is_active')
    list_filter = ('is_premium', 'is_active')

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'score', 'created_at')
