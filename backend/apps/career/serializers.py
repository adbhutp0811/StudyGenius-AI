from rest_framework import serializers
from .models import SkillAssessment, CareerRecommendation, IndustryTrend, SalaryInsight


class SkillAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillAssessment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'overall_score', 'recommendations',
                           'is_completed', 'started_at', 'completed_at', 'created_at')


class SkillAssessmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillAssessment
        fields = ('id', 'title', 'category', 'overall_score', 'is_completed',
                  'time_taken_minutes', 'started_at', 'completed_at', 'created_at')


class CareerRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerRecommendation
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')


class IndustryTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndustryTrend
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class SalaryInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryInsight
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class StartAssessmentSerializer(serializers.Serializer):
    category = serializers.CharField()
    skill_level = serializers.ChoiceField(choices=['beginner', 'intermediate', 'advanced'], default='beginner')
    skills = serializers.ListField(child=serializers.CharField(), required=False)


class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.CharField()
    answer = serializers.CharField()
