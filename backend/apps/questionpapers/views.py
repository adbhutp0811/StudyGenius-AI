from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import QuestionPaper, QuestionBank, Subject
from .serializers import (
    QuestionPaperSerializer, QuestionPaperListSerializer,
    QuestionBankSerializer, SubjectSerializer,
    GeneratePaperSerializer
)
from ..ai_services.gemini_service import GeminiService
from django.http import HttpResponse


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = (permissions.AllowAny,)
    search_fields = ['name', 'description']


class QuestionPaperViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['difficulty', 'is_generated']
    search_fields = ['title', 'subject_name']
    ordering_fields = ['created_at', 'total_marks']

    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionPaperListSerializer
        return QuestionPaperSerializer

    def get_queryset(self):
        return QuestionPaper.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = GeneratePaperSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        gemini = GeminiService()
        paper_data = gemini.generate_question_paper(
            subject=serializer.validated_data['subject'],
            syllabus=serializer.validated_data.get('syllabus', ''),
            difficulty=serializer.validated_data['difficulty'],
            num_mcq=serializer.validated_data['num_mcq'],
            num_short_answer=serializer.validated_data['num_short_answer'],
            num_long_answer=serializer.validated_data['num_long_answer'],
        )

        questions = paper_data.get('questions', [])
        total_questions = len(questions)
        total_marks = sum(q.get('marks', 1) for q in questions)

        subject_obj, _ = Subject.objects.get_or_create(
            name=serializer.validated_data['subject']
        )

        paper = QuestionPaper.objects.create(
            user=request.user,
            title=f"{serializer.validated_data['subject']} - {serializer.validated_data['difficulty'].title()}",
            subject=subject_obj,
            subject_name=serializer.validated_data['subject'],
            syllabus=serializer.validated_data.get('syllabus', ''),
            difficulty=serializer.validated_data['difficulty'],
            total_questions=total_questions,
            total_marks=total_marks,
            time_duration_minutes=serializer.validated_data['time_duration_minutes'],
            questions=questions,
            is_generated=True,
        )

        return Response(QuestionPaperSerializer(paper).data, status=201)

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        paper = self.get_object()
        from ..ai_services.pdf_generator import generate_question_paper_pdf
        pdf_buffer = generate_question_paper_pdf(paper)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{paper.title}.pdf"'
        return response


class QuestionBankViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = QuestionBankSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['question_type', 'difficulty', 'subject']
    search_fields = ['question', 'tags']
    ordering_fields = ['created_at', 'marks']

    def get_queryset(self):
        return QuestionBank.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
