from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import CAREER_GOALS, Roadmap, Milestone, DailyPlan, Resource
from .serializers import (
    RoadmapSerializer, RoadmapListSerializer,
    MilestoneSerializer, DailyPlanSerializer,
    ResourceSerializer, GenerateRoadmapSerializer
)
from ..ai_services.roadmap_generator import RoadmapGenerator


class RoadmapViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_completed', 'career_goal']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at', 'progress']

    def get_serializer_class(self):
        if self.action == 'list':
            return RoadmapListSerializer
        return RoadmapSerializer

    def get_queryset(self):
        return Roadmap.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = GenerateRoadmapSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        generator = RoadmapGenerator()
        roadmap_data = generator.generate(
            career_goal=serializer.validated_data['career_goal'],
            duration_months=serializer.validated_data['duration_months'],
            skill_level=serializer.validated_data.get('skill_level', 'beginner'),
            custom_goal=serializer.validated_data.get('custom_goal', ''),
        )

        roadmap = Roadmap.objects.create(
            user=request.user,
            title=f"{dict(CAREER_GOALS).get(serializer.validated_data['career_goal'], 'Career')} Roadmap",
            career_goal=serializer.validated_data['career_goal'],
            custom_goal=serializer.validated_data.get('custom_goal', ''),
            duration_months=serializer.validated_data['duration_months'],
            milestones=roadmap_data.get('milestones', []),
            resources=roadmap_data.get('resources', []),
        )

        for i, milestone_data in enumerate(roadmap_data.get('milestones', [])):
            Milestone.objects.create(
                roadmap=roadmap,
                title=milestone_data.get('title', f'Milestone {i+1}'),
                description=milestone_data.get('description', ''),
                order=i,
                resources=milestone_data.get('resources', []),
                duration_days=milestone_data.get('duration_days', 7),
            )

        for resource_data in roadmap_data.get('resources', []):
            Resource.objects.create(
                roadmap=roadmap,
                title=resource_data.get('title', 'Resource'),
                description=resource_data.get('description', ''),
                url=resource_data.get('url', ''),
                resource_type=resource_data.get('resource_type', 'other'),
                is_free=resource_data.get('is_free', True),
            )

        return Response(RoadmapSerializer(roadmap).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        roadmap = self.get_object()
        completed = Milestone.objects.filter(roadmap=roadmap, status='completed').count()
        total = Milestone.objects.filter(roadmap=roadmap).count()
        if total > 0:
            roadmap.progress = round((completed / total) * 100, 2)
        if roadmap.progress >= 100:
            roadmap.is_completed = True
        roadmap.save()
        return Response({'progress': roadmap.progress, 'is_completed': roadmap.is_completed})

    @action(detail=True, methods=['post'])
    def generate_daily_plan(self, request, pk=None):
        roadmap = self.get_object()
        milestone_id = request.data.get('milestone_id')
        if not milestone_id:
            return Response({'error': 'milestone_id is required'}, status=400)

        try:
            milestone = Milestone.objects.get(id=milestone_id, roadmap=roadmap)
        except Milestone.DoesNotExist:
            return Response({'error': 'Milestone not found'}, status=404)

        from ..ai_services.roadmap_generator import RoadmapGenerator
        generator = RoadmapGenerator()
        plan = generator.generate_daily_plan(milestone)

        DailyPlan.objects.filter(milestone=milestone, date=timezone.now().date()).delete()
        daily_plan = DailyPlan.objects.create(
            milestone=milestone,
            date=timezone.now().date(),
            tasks=plan.get('tasks', []),
            notes=plan.get('notes', ''),
        )

        return Response(DailyPlanSerializer(daily_plan).data)

    @action(detail=True, methods=['get'])
    def daily_plans(self, request, pk=None):
        roadmap = self.get_object()
        milestone_id = request.query_params.get('milestone_id')
        plans = DailyPlan.objects.filter(milestone__roadmap=roadmap)
        if milestone_id:
            plans = plans.filter(milestone_id=milestone_id)
        page = self.paginate_queryset(plans)
        if page:
            serializer = DailyPlanSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = DailyPlanSerializer(plans, many=True)
        return Response(serializer.data)


class MilestoneViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = MilestoneSerializer

    def get_queryset(self):
        return Milestone.objects.filter(roadmap__user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        milestone = self.get_object()
        milestone.status = 'completed'
        milestone.completed_at = timezone.now()
        milestone.save()
        roadmap = milestone.roadmap
        completed = Milestone.objects.filter(roadmap=roadmap, status='completed').count()
        total = Milestone.objects.filter(roadmap=roadmap).count()
        roadmap.progress = round((completed / total) * 100, 2) if total > 0 else 0
        if roadmap.progress >= 100:
            roadmap.is_completed = True
        roadmap.save()
        return Response(MilestoneSerializer(milestone).data)


class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['resource_type', 'is_free', 'is_completed']
    search_fields = ['title', 'description']

    def get_queryset(self):
        return Resource.objects.filter(roadmap__user=self.request.user)
