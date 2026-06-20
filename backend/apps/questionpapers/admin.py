from django.contrib import admin
from .models import QuestionPaper, QuestionBank, Subject

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'subject_name', 'difficulty', 'total_questions', 'total_marks', 'created_at')
    list_filter = ('difficulty', 'is_generated')

@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    list_display = ('question_type', 'difficulty', 'marks', 'subject', 'created_at')
    list_filter = ('question_type', 'difficulty')
    search_fields = ('question',)
