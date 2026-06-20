from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ChatSession, ChatMessage, BookmarkedAnswer
from .serializers import (
    ChatSessionSerializer, ChatSessionListSerializer,
    ChatMessageSerializer, BookmarkedAnswerSerializer,
    DoubtQuerySerializer
)
from ..ai_services.gemini_service import GeminiService


class ChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['subject', 'is_active']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def ask(self, request):
        serializer = DoubtQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data.get('session_id')
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({'error': 'Session not found'}, status=404)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=serializer.validated_data['question'][:50],
                subject=serializer.validated_data['subject'],
            )

        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=serializer.validated_data['question'],
            code_snippet=serializer.validated_data.get('code_snippet', ''),
            code_language=serializer.validated_data.get('code_language', ''),
        )

        gemini = GeminiService()
        chat_history = [
            {'role': m.role, 'content': m.content}
            for m in session.messages.all()[:10]
        ]
        response_text = gemini.answer_doubt(
            question=serializer.validated_data['question'],
            subject=serializer.validated_data['subject'],
            chat_history=chat_history,
            code=serializer.validated_data.get('code_snippet', ''),
        )

        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response_text,
        )

        return Response({
            'session': ChatSessionSerializer(session).data,
            'user_message': ChatMessageSerializer(user_message).data,
            'assistant_message': ChatMessageSerializer(assistant_message).data,
        })

    @action(detail=False, methods=['post'])
    def ask_with_image(self, request):
        question = request.data.get('question', '')
        image = request.FILES.get('image')
        subject = request.data.get('subject', 'other')
        session_id = request.data.get('session_id', '')

        if not image:
            return Response({'error': 'Image is required'}, status=400)

        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({'error': 'Session not found'}, status=404)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                title=f"Image Question: {question[:50]}" if question else "Image Question",
                subject=subject,
            )

        user_message = ChatMessage.objects.create(
            session=session,
            role='user',
            content=question or 'Analyze this image',
            image=image,
        )

        gemini = GeminiService()
        response_text = gemini.analyze_image(image, question)

        assistant_message = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response_text,
        )

        return Response({
            'session': ChatSessionSerializer(session).data,
            'user_message': ChatMessageSerializer(user_message).data,
            'assistant_message': ChatMessageSerializer(assistant_message).data,
        })

    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        message_id = request.data.get('message_id')
        if not message_id:
            return Response({'error': 'message_id is required'}, status=400)

        session = self.get_object()
        try:
            message = ChatMessage.objects.get(id=message_id, session=session)
        except ChatMessage.DoesNotExist:
            return Response({'error': 'Message not found'}, status=404)

        bookmark, created = BookmarkedAnswer.objects.get_or_create(
            user=request.user,
            message=message,
            defaults={'note': request.data.get('note', '')}
        )
        if not created:
            bookmark.delete()
            message.is_bookmarked = False
            message.save()
            return Response({'bookmarked': False})

        message.is_bookmarked = True
        message.save()
        return Response({'bookmarked': True, 'bookmark': BookmarkedAnswerSerializer(bookmark).data})


class BookmarkedAnswerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BookmarkedAnswerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['message__content', 'note', 'tags']

    def get_queryset(self):
        return BookmarkedAnswer.objects.filter(user=self.request.user)

    @action(detail=True, methods=['delete'])
    def remove(self, request, pk=None):
        bookmark = self.get_object()
        bookmark.delete()
        return Response(status=204)
