from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import PDFDocument, PDFChatSession, PDFChatMessage, DocumentHighlight
from .serializers import (
    PDFDocumentSerializer, PDFDocumentListSerializer,
    PDFChatSessionSerializer, PDFChatSessionListSerializer,
    PDFChatMessageSerializer, DocumentHighlightSerializer,
    PDFQuerySerializer
)
from ..ai_services.pdf_service import PDFService
from ..ai_services.gemini_service import GeminiService


class PDFDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_processed']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'file_size']

    def get_serializer_class(self):
        if self.action == 'list':
            return PDFDocumentListSerializer
        return PDFDocumentSerializer

    def get_queryset(self):
        return PDFDocument.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user)

        pdf_service = PDFService()
        result = pdf_service.process_pdf(instance)
        instance.content_text = result.get('content', '')
        instance.page_count = result.get('page_count', 0)
        instance.file_size = instance.file.size
        instance.is_processed = True
        instance.save()

        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        document = self.get_object()
        return Response({
            'id': str(document.id),
            'title': document.title,
            'content': document.content_text,
            'page_count': document.page_count,
        })

    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        document = self.get_object()
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query is required'}, status=400)

        results = []
        content = document.content_text
        paragraphs = content.split('\n\n')
        for i, para in enumerate(paragraphs):
            if query.lower() in para.lower():
                results.append({
                    'paragraph_index': i,
                    'text': para[:500] + '...' if len(para) > 500 else para,
                })

        return Response({'results': results, 'total': len(results)})


class PDFChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PDFChatSessionListSerializer
        return PDFChatSessionSerializer

    def get_queryset(self):
        return PDFChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def ask(self, request):
        serializer = PDFQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']
        session_id = serializer.validated_data.get('session_id', '')
        document_ids = serializer.validated_data.get('document_ids', [])

        if session_id:
            try:
                session = PDFChatSession.objects.get(id=session_id, user=request.user)
            except PDFChatSession.DoesNotExist:
                return Response({'error': 'Session not found'}, status=404)
        else:
            docs = PDFDocument.objects.filter(id__in=document_ids, user=request.user)
            if not docs.exists():
                return Response({'error': 'No valid documents found'}, status=400)
            session = PDFChatSession.objects.create(
                user=request.user,
                title=f"Chat: {question[:50]}",
            )
            session.pdf_documents.set(docs)

        user_message = PDFChatMessage.objects.create(
            session=session,
            role='user',
            content=question,
        )

        context = ''
        for doc in session.pdf_documents.all():
            context += f"\n\n--- Document: {doc.title} ---\n{doc.content_text[:5000]}\n"

        chat_history = [
            {'role': m.role, 'content': m.content}
            for m in session.messages.all()[:6]
        ]

        gemini = GeminiService()
        response_text, relevant_sections = gemini.answer_pdf_question(
            question=question,
            context=context,
            chat_history=chat_history,
        )

        assistant_message = PDFChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response_text,
            relevant_sections=relevant_sections,
        )

        return Response({
            'session': PDFChatSessionSerializer(session).data,
            'user_message': PDFChatMessageSerializer(user_message).data,
            'assistant_message': PDFChatMessageSerializer(assistant_message).data,
        })


class DocumentHighlightViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DocumentHighlightSerializer

    def get_queryset(self):
        return DocumentHighlight.objects.filter(
            document__user=self.request.user,
            user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def by_document(self, request):
        document_id = request.query_params.get('document_id')
        if not document_id:
            return Response({'error': 'document_id is required'}, status=400)
        highlights = self.get_queryset().filter(document_id=document_id)
        serializer = self.get_serializer(highlights, many=True)
        return Response(serializer.data)
