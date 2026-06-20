from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Resume, ResumeTemplate, ResumeAnalysis
from .serializers import (
    ResumeSerializer, ResumeListSerializer,
    ResumeTemplateSerializer, ResumeAnalysisSerializer
)
from ..ai_services.gemini_service import GeminiService
from ..ai_services.resume_analyzer import ResumeAnalyzer
import json


class ResumeTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ResumeTemplate.objects.filter(is_active=True)
    serializer_class = ResumeTemplateSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_premium']
    search_fields = ['name', 'description']


class ResumeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_complete']
    search_fields = ['title', 'full_name']
    ordering_fields = ['created_at', 'updated_at', 'ats_score']

    def get_serializer_class(self):
        if self.action == 'list':
            return ResumeListSerializer
        return ResumeSerializer

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_summary(self, request, pk=None):
        resume = self.get_object()
        gemini = GeminiService()
        skills_text = ', '.join(resume.skills) if resume.skills else ''
        experience_text = ''
        for exp in resume.experience:
            experience_text += f"{exp.get('title', '')} at {exp.get('company', '')}\n"
        prompt = f"Write a professional resume summary for a candidate with these skills: {skills_text}. Experience: {experience_text}. Keep it concise (3-4 sentences) and professional."
        summary = gemini.generate_text(prompt)
        resume.professional_summary = summary
        resume.save()
        return Response({'professional_summary': summary})

    @action(detail=True, methods=['post'])
    def suggest_skills(self, request, pk=None):
        resume = self.get_object()
        gemini = GeminiService()
        current_skills = ', '.join(resume.skills) if resume.skills else 'experience'
        prompt = f"Based on a resume with skills: {current_skills}, suggest 10 relevant skills to add. Return as a comma-separated list."
        suggestions = gemini.generate_text(prompt)
        skills_list = [s.strip() for s in suggestions.split(',') if s.strip()]
        return Response({'suggested_skills': skills_list})

    @action(detail=True, methods=['post'])
    def enhance_experience(self, request, pk=None):
        resume = self.get_object()
        experience_index = request.data.get('index')
        if experience_index is None:
            return Response({'error': 'Experience index is required'}, status=400)
        try:
            exp = resume.experience[int(experience_index)]
        except (IndexError, ValueError):
            return Response({'error': 'Invalid index'}, status=400)

        gemini = GeminiService()
        description = exp.get('description', '')
        prompt = f"Enhance this resume experience description to be more impactful and professional: '{description}'. Make it achievement-oriented and quantify results where possible."
        enhanced = gemini.generate_text(prompt)
        return Response({'enhanced_description': enhanced})

    @action(detail=True, methods=['post'])
    def analyze_score(self, request, pk=None):
        resume = self.get_object()
        analyzer = ResumeAnalyzer()
        analysis = analyzer.analyze(resume)
        ResumeAnalysis.objects.create(resume=resume, **analysis)
        resume.ats_score = analysis.get('score', 0)
        resume.save()
        serializer = ResumeAnalysisSerializer(data=analysis)
        serializer.is_valid(raise_exception=True)
        return Response(analysis)

    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        resume = self.get_object()
        analysis = ResumeAnalysis.objects.filter(resume=resume).first()
        if not analysis:
            return Response({'detail': 'No analysis found. Run analyze_score first.'}, status=404)
        return Response(ResumeAnalysisSerializer(analysis).data)

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        from django.http import FileResponse
        import tempfile
        from ..ai_services.pdf_generator import generate_resume_pdf
        resume = self.get_object()
        pdf_buffer = generate_resume_pdf(resume)
        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=f'{resume.full_name.replace(" ", "_")}_Resume.pdf',
            content_type='application/pdf'
        )
