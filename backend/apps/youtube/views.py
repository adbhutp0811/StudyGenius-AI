from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import VideoSummary, SavedNote
from .serializers import (
    VideoSummarySerializer, VideoSummaryListSerializer,
    SavedNoteSerializer, SummarizeVideoSerializer
)
from ..ai_services.youtube_service import YouTubeService


class VideoSummaryViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'channel_name']
    ordering_fields = ['created_at', 'duration']

    def get_serializer_class(self):
        if self.action == 'list':
            return VideoSummaryListSerializer
        return VideoSummarySerializer

    def get_queryset(self):
        return VideoSummary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def summarize(self, request):
        serializer = SummarizeVideoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = serializer.validated_data['url']
        language = serializer.validated_data.get('language', 'en')

        youtube_service = YouTubeService()
        video_data = youtube_service.extract_and_summarize(url, language)

        if 'error' in video_data:
            return Response({'error': video_data['error']}, status=status.HTTP_400_BAD_REQUEST)

        summary = VideoSummary.objects.create(
            user=request.user,
            title=video_data.get('title', 'Video Summary'),
            url=url,
            video_id=video_data.get('video_id', ''),
            channel_name=video_data.get('channel_name', ''),
            duration=video_data.get('duration', 0),
            thumbnail_url=video_data.get('thumbnail_url', ''),
            transcript=video_data.get('transcript', ''),
            summary=video_data.get('summary', ''),
            key_points=video_data.get('key_points', []),
            notes=video_data.get('notes', ''),
            quiz=video_data.get('quiz', []),
            language=language,
        )

        return Response(VideoSummarySerializer(summary).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def generate_quiz(self, request, pk=None):
        video = self.get_object()
        from ..ai_services.gemini_service import GeminiService
        gemini = GeminiService()
        quiz = gemini.generate_quiz_from_content(video.summary, video.key_points)
        video.quiz = quiz
        video.save()
        return Response({'quiz': quiz})

    @action(detail=True, methods=['post'])
    def save_note(self, request, pk=None):
        video = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required'}, status=400)
        note = SavedNote.objects.create(video_summary=video, content=content)
        return Response(SavedNoteSerializer(note).data, status=201)

    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        video = self.get_object()
        notes = SavedNote.objects.filter(video_summary=video)
        serializer = SavedNoteSerializer(notes, many=True)
        return Response(serializer.data)
