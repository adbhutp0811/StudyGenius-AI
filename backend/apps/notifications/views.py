from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Notification, NotificationPreference, ActivityLog
from .serializers import (
    NotificationSerializer, NotificationPreferenceSerializer,
    ActivityLogSerializer, MarkReadSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'is_read', 'is_archived']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, is_archived=False)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get('all'):
            updated = Notification.objects.filter(
                user=request.user, is_read=False
            ).update(is_read=True, read_at=timezone.now())
            return Response({'marked_read': updated})

        notification_ids = serializer.validated_data.get('notification_ids', [])
        updated = Notification.objects.filter(
            id__in=notification_ids, user=request.user
        ).update(is_read=True, read_at=timezone.now())
        return Response({'marked_read': updated})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['get'])
    def recent(self, request):
        notifications = self.get_queryset()[:10]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        notification = self.get_object()
        notification.is_archived = True
        notification.save()
        return Response(status=204)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NotificationPreferenceSerializer

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def get_object(self):
        pref, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return pref


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ActivityLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['activity_type']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        logs = self.get_queryset()[:20]
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        logs = ActivityLog.objects.filter(user=request.user)
        total = logs.count()
        by_type = {}
        for log in logs.values('activity_type').annotate(count=models.Count('id')):
            by_type[log['activity_type']] = log['count']
        return Response({
            'total_activities': total,
            'by_type': by_type,
        })
