from django.contrib import admin
from .models import Roadmap, Milestone, DailyPlan, Resource

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'career_goal', 'progress', 'is_active', 'created_at')
    list_filter = ('career_goal', 'is_active', 'is_completed')
    search_fields = ('title', 'user__email')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'status', 'order', 'duration_days')
    list_filter = ('status',)

@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    list_display = ('milestone', 'date', 'is_completed')

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'resource_type', 'is_free', 'is_completed')
    list_filter = ('resource_type', 'is_free')
