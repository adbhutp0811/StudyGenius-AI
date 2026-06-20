from django.db import models
from django.conf import settings
import uuid

SKILL_LEVELS = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]

INTEREST_AREAS = [
    ('technology', 'Technology'),
    ('healthcare', 'Healthcare'),
    ('finance', 'Finance'),
    ('education', 'Education'),
    ('creative', 'Creative Arts'),
    ('business', 'Business'),
    ('science', 'Science'),
    ('engineering', 'Engineering'),
    ('other', 'Other'),
]

class SkillAssessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='skill_assessments')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    skills_evaluated = models.JSONField(default=list)
    questions = models.JSONField(default=list)
    answers = models.JSONField(default=dict, blank=True)
    scores = models.JSONField(default=dict, blank=True)
    overall_score = models.FloatField(default=0.0)
    recommendations = models.JSONField(default=list, blank=True)
    time_taken_minutes = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'skill_assessments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.email}"


class CareerRecommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='career_recommendations')
    assessment = models.ForeignKey(SkillAssessment, on_delete=models.SET_NULL, null=True, blank=True)
    career_options = models.JSONField(default=list)
    skill_gaps = models.JSONField(default=list)
    suggested_courses = models.JSONField(default=list)
    industry_insights = models.JSONField(default=dict)
    salary_insights = models.JSONField(default=dict)
    career_path = models.JSONField(default=list)
    internship_recommendations = models.JSONField(default=list)
    project_recommendations = models.JSONField(default=list)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'career_recommendations'
        ordering = ['-created_at']

    def __str__(self):
        return f"Career Recommendation - {self.user.email}"


class IndustryTrend(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    industry = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    trend_data = models.JSONField(default=dict)
    source = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'industry_trends'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.industry} - {self.title}"


class SalaryInsight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=50)
    salary_range = models.CharField(max_length=100)
    currency = models.CharField(max_length=10, default='USD')
    location = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'salary_insights'
        ordering = ['role']

    def __str__(self):
        return f"{self.role} - {self.salary_range}"
