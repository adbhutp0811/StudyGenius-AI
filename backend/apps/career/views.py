from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import SkillAssessment, CareerRecommendation, IndustryTrend, SalaryInsight
from .serializers import (
    SkillAssessmentSerializer, SkillAssessmentListSerializer,
    CareerRecommendationSerializer, IndustryTrendSerializer,
    SalaryInsightSerializer, StartAssessmentSerializer
)
from ..ai_services.gemini_service import GeminiService
from ..ai_services.career_service import CareerService


class SkillAssessmentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_completed']
    search_fields = ['title']
    ordering_fields = ['created_at', 'overall_score']

    def get_serializer_class(self):
        if self.action == 'list':
            return SkillAssessmentListSerializer
        return SkillAssessmentSerializer

    def get_queryset(self):
        return SkillAssessment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def start(self, request):
        serializer = StartAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        gemini = GeminiService()
        assessment_data = gemini.generate_assessment(
            category=serializer.validated_data['category'],
            skill_level=serializer.validated_data.get('skill_level', 'beginner'),
            skills=serializer.validated_data.get('skills', []),
        )

        assessment = SkillAssessment.objects.create(
            user=request.user,
            title=f"{serializer.validated_data['category'].title()} Assessment",
            category=serializer.validated_data['category'],
            skills_evaluated=serializer.validated_data.get('skills', []),
            questions=assessment_data.get('questions', []),
        )

        return Response(SkillAssessmentSerializer(assessment).data, status=201)

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        assessment = self.get_object()
        if assessment.is_completed:
            return Response({'error': 'Assessment already completed'}, status=400)

        question_id = request.data.get('question_id')
        answer = request.data.get('answer')
        if not question_id or answer is None:
            return Response({'error': 'question_id and answer are required'}, status=400)

        answers = assessment.answers
        answers[question_id] = answer
        assessment.answers = answers
        assessment.save()

        return Response({'message': 'Answer saved', 'question_id': question_id})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        assessment = self.get_object()
        if assessment.is_completed:
            return Response({'error': 'Already completed'}, status=400)

        gemini = GeminiService()
        results = gemini.evaluate_assessment(assessment.questions, assessment.answers)

        assessment.scores = results.get('scores', {})
        assessment.overall_score = results.get('overall_score', 0)
        assessment.recommendations = results.get('recommendations', [])
        assessment.is_completed = True
        assessment.completed_at = timezone.now()
        assessment.save()

        career_service = CareerService()
        recommendation = career_service.generate_recommendation(
            assessment=assessment,
            scores=results,
        )

        return Response({
            'assessment': SkillAssessmentSerializer(assessment).data,
            'recommendation': CareerRecommendationSerializer(recommendation).data if recommendation else None,
        })

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        assessment = self.get_object()
        if not assessment.is_completed:
            return Response({'error': 'Assessment not completed yet'}, status=400)

        recommendations = CareerRecommendation.objects.filter(
            user=request.user,
            assessment=assessment
        ).first()

        return Response({
            'assessment': SkillAssessmentSerializer(assessment).data,
            'recommendation': CareerRecommendationSerializer(recommendations).data if recommendations else None,
        })


class CareerRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CareerRecommendationSerializer

    def get_queryset(self):
        return CareerRecommendation.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        recommendation = CareerRecommendation.objects.filter(
            user=request.user
        ).first()
        if not recommendation:
            return Response({'detail': 'No recommendations found'}, status=404)
        return Response(CareerRecommendationSerializer(recommendation).data)


class IndustryTrendViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IndustryTrend.objects.filter(is_active=True)
    serializer_class = IndustryTrendSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['industry']
    search_fields = ['title', 'industry', 'description']


class SalaryInsightViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SalaryInsight.objects.all()
    serializer_class = SalaryInsightSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['industry', 'experience_level', 'location']
    search_fields = ['role', 'industry']
