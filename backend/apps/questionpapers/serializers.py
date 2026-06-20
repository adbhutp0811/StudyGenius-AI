from rest_framework import serializers
from .models import QuestionPaper, QuestionBank, Subject, DIFFICULTY_LEVELS


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class QuestionBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class QuestionPaperListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = QuestionPaper
        fields = ('id', 'title', 'subject_name', 'difficulty', 'total_questions',
                  'total_marks', 'time_duration_minutes', 'is_generated', 'created_at')


class QuestionPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionPaper
        fields = '__all__'
        read_only_fields = ('id', 'user', 'total_questions', 'total_marks',
                           'is_generated', 'created_at', 'updated_at')


class GeneratePaperSerializer(serializers.Serializer):
    subject = serializers.CharField()
    syllabus = serializers.CharField(required=False, allow_blank=True)
    difficulty = serializers.ChoiceField(choices=[d[0] for d in DIFFICULTY_LEVELS], default='medium')
    num_mcq = serializers.IntegerField(default=5, min_value=0)
    num_short_answer = serializers.IntegerField(default=5, min_value=0)
    num_long_answer = serializers.IntegerField(default=3, min_value=0)
    time_duration_minutes = serializers.IntegerField(default=60)
    include_answers = serializers.BooleanField(default=True)
