from rest_framework import serializers
from .models import Resume, ResumeTemplate, ResumeAnalysis


class ResumeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeTemplate
        fields = '__all__'


class ResumeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', 'title', 'full_name', 'template', 'ats_score',
                  'is_complete', 'created_at', 'updated_at')


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('id', 'user', 'ats_score', 'is_complete', 'created_at', 'updated_at')


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = '__all__'
        read_only_fields = ('id', 'created_at')
