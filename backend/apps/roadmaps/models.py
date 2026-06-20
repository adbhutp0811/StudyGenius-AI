from django.db import models
from django.conf import settings
import uuid

CAREER_GOALS = [
    ('web_development', 'Web Development'),
    ('ai_ml', 'AI/ML'),
    ('data_science', 'Data Science'),
    ('cybersecurity', 'Cybersecurity'),
    ('devops', 'DevOps'),
    ('mobile_development', 'Mobile Development'),
    ('cloud_computing', 'Cloud Computing'),
    ('blockchain', 'Blockchain'),
    ('other', 'Other'),
]

class Roadmap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roadmaps')
    title = models.CharField(max_length=200)
    career_goal = models.CharField(max_length=50, choices=CAREER_GOALS)
    custom_goal = models.CharField(max_length=200, blank=True)
    duration_months = models.IntegerField(default=6)
    milestones = models.JSONField(default=list)
    resources = models.JSONField(default=list, blank=True)
    progress = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roadmaps'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.get_career_goal_display()}"


class Milestone(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='milestone_set')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    resources = models.JSONField(default=list, blank=True)
    duration_days = models.IntegerField(default=7)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'milestones'
        ordering = ['order']

    def __str__(self):
        return self.title


class DailyPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='daily_plans')
    date = models.DateField()
    tasks = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_plans'
        unique_together = ['milestone', 'date']
        ordering = ['date']


class Resource(models.Model):
    RESOURCE_TYPES = [
        ('course', 'Course'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('book', 'Book'),
        ('documentation', 'Documentation'),
        ('tool', 'Tool'),
        ('project', 'Project'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='resource_set')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    is_free = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'resources'

    def __str__(self):
        return self.title
