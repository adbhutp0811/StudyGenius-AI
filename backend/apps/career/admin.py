from django.contrib import admin
from .models import SkillAssessment, CareerRecommendation, IndustryTrend, SalaryInsight

@admin.register(SkillAssessment)
class SkillAssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'overall_score', 'is_completed', 'created_at')
    list_filter = ('category', 'is_completed')

@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')

@admin.register(IndustryTrend)
class IndustryTrendAdmin(admin.ModelAdmin):
    list_display = ('industry', 'title', 'is_active', 'created_at')
    list_filter = ('industry', 'is_active')

@admin.register(SalaryInsight)
class SalaryInsightAdmin(admin.ModelAdmin):
    list_display = ('role', 'industry', 'experience_level', 'salary_range', 'location')
    list_filter = ('industry', 'experience_level', 'location')
