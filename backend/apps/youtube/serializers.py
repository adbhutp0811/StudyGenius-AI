from rest_framework import serializers
from .models import VideoSummary, SavedNote


class VideoSummaryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSummary
        fields = ('id', 'title', 'url', 'channel_name', 'duration',
                  'thumbnail_url', 'language', 'created_at')


class VideoSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoSummary
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')


class SavedNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedNote
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class SummarizeVideoSerializer(serializers.Serializer):
    url = serializers.URLField()
    language = serializers.CharField(default='en', required=False)
