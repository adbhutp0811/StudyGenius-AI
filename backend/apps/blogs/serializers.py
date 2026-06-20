from rest_framework import serializers
from .models import Blog, BlogVersion, SEOSuggestion


class BlogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('id', 'title', 'excerpt', 'reading_time', 'word_count',
                  'status', 'is_generated', 'created_at', 'updated_at', 'published_at')


class SEOSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOSuggestion
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):
    seo_suggestions = SEOSuggestionSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ('id', 'user', 'reading_time', 'word_count',
                           'is_generated', 'grammar_checked', 'created_at',
                           'updated_at', 'published_at')


class BlogVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogVersion
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class GenerateBlogSerializer(serializers.Serializer):
    keywords = serializers.ListField(child=serializers.CharField())
    title = serializers.CharField(required=False, allow_blank=True)
    tone = serializers.ChoiceField(
        choices=['professional', 'conversational', 'academic', 'creative', 'technical'],
        default='professional'
    )
    length = serializers.ChoiceField(
        choices=['short', 'medium', 'long'],
        default='medium'
    )
    target_audience = serializers.CharField(required=False, allow_blank=True)


class GrammarCheckSerializer(serializers.Serializer):
    content = serializers.CharField()
