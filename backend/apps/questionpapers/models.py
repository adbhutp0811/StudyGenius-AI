from django.db import models
from django.conf import settings
import uuid

DIFFICULTY_LEVELS = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
]

QUESTION_TYPES = [
    ('mcq', 'Multiple Choice'),
    ('short_answer', 'Short Answer'),
    ('long_answer', 'Long Answer'),
    ('true_false', 'True/False'),
    ('fill_blanks', 'Fill in the Blanks'),
]

class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subjects'

    def __str__(self):
        return self.name


class QuestionPaper(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='question_papers')
    title = models.CharField(max_length=500)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    subject_name = models.CharField(max_length=200, blank=True)
    syllabus = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='medium')
    total_questions = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    time_duration_minutes = models.IntegerField(default=60)
    questions = models.JSONField(default=list)
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'question_papers'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class QuestionBank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='question_bank')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS)
    question = models.TextField()
    options = models.JSONField(default=list, blank=True)
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True)
    marks = models.IntegerField(default=1)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'question_bank'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_question_type_display()}: {self.question[:50]}"
