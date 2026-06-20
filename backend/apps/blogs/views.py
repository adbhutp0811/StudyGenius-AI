from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Blog, BlogVersion, SEOSuggestion
from .serializers import (
    BlogSerializer, BlogListSerializer,
    BlogVersionSerializer, SEOSuggestionSerializer,
    GenerateBlogSerializer, GrammarCheckSerializer
)
from ..ai_services.gemini_service import GeminiService
import markdown
from django.http import HttpResponse


class BlogViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'is_generated']
    search_fields = ['title', 'content', 'keywords']
    ordering_fields = ['created_at', 'updated_at', 'published_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return BlogListSerializer
        return BlogSerializer

    def get_queryset(self):
        return Blog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = GenerateBlogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        gemini = GeminiService()
        blog_data = gemini.generate_blog(
            keywords=serializer.validated_data['keywords'],
            title=serializer.validated_data.get('title', ''),
            tone=serializer.validated_data.get('tone', 'professional'),
            length=serializer.validated_data.get('length', 'medium'),
            target_audience=serializer.validated_data.get('target_audience', ''),
        )

        content = blog_data.get('content', '')
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)

        blog = Blog.objects.create(
            user=request.user,
            title=blog_data.get('title', 'Generated Blog'),
            content=content,
            excerpt=blog_data.get('excerpt', ''),
            keywords=serializer.validated_data['keywords'],
            seo_title=blog_data.get('seo_title', ''),
            seo_description=blog_data.get('seo_description', ''),
            seo_tags=blog_data.get('seo_tags', []),
            word_count=word_count,
            reading_time=reading_time,
            is_generated=True,
        )

        BlogVersion.objects.create(
            blog=blog,
            title=blog.title,
            content=blog.content,
            version_number=1,
        )

        return Response(BlogSerializer(blog).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def optimize_seo(self, request, pk=None):
        blog = self.get_object()
        gemini = GeminiService()
        seo_data = gemini.optimize_seo(blog.title, blog.content, blog.keywords)

        if seo_data.get('seo_title'):
            blog.seo_title = seo_data['seo_title']
        if seo_data.get('seo_description'):
            blog.seo_description = seo_data['seo_description']
        if seo_data.get('seo_tags'):
            blog.seo_tags = seo_data['seo_tags']
        blog.save()

        SEOSuggestion.objects.filter(blog=blog).delete()
        suggestions = seo_data.get('suggestions', [])
        for suggestion in suggestions:
            SEOSuggestion.objects.create(
                blog=blog,
                suggestion_type=suggestion.get('type', 'general'),
                current_value=suggestion.get('current', ''),
                suggested_value=suggestion.get('suggested', ''),
                reason=suggestion.get('reason', ''),
            )

        return Response(BlogSerializer(blog).data)

    @action(detail=True, methods=['post'])
    def grammar_check(self, request, pk=None):
        blog = self.get_object()
        gemini = GeminiService()
        result = gemini.check_grammar(blog.content)
        blog.grammar_checked = True
        blog.save()

        if result.get('corrected_content'):
            BlogVersion.objects.create(
                blog=blog,
                title=blog.title,
                content=result['corrected_content'],
                version_number=blog.versions.count() + 1,
            )

        return Response(result)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        blog = self.get_object()
        blog.status = 'published'
        blog.published_at = timezone.now()
        blog.save()
        return Response(BlogSerializer(blog).data)

    @action(detail=True, methods=['post'])
    def save_version(self, request, pk=None):
        blog = self.get_object()
        version = BlogVersion.objects.create(
            blog=blog,
            title=request.data.get('title', blog.title),
            content=request.data.get('content', blog.content),
            version_number=blog.versions.count() + 1,
        )
        return Response(BlogVersionSerializer(version).data, status=201)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        blog = self.get_object()
        versions = blog.versions.all()
        page = self.paginate_queryset(versions)
        if page:
            serializer = BlogVersionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BlogVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        blog = self.get_object()
        export_format = request.query_params.get('format', 'markdown')

        if export_format == 'markdown':
            content = f"# {blog.title}\n\n{blog.content}"
            response = HttpResponse(content, content_type='text/markdown')
            response['Content-Disposition'] = f'attachment; filename="{blog.title}.md"'
            return response
        elif export_format == 'html':
            html = markdown.markdown(blog.content)
            content = f"<h1>{blog.title}</h1>\n{html}"
            response = HttpResponse(content, content_type='text/html')
            response['Content-Disposition'] = f'attachment; filename="{blog.title}.html"'
            return response
        elif export_format == 'pdf':
            from ..ai_services.pdf_generator import generate_blog_pdf
            pdf_buffer = generate_blog_pdf(blog)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{blog.title}.pdf"'
            return response

        return Response({'error': 'Invalid format. Use markdown, html, or pdf.'}, status=400)
