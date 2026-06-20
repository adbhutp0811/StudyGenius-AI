from rest_framework import serializers
from .models import Notification, NotificationPreference, ActivityLog


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'read_at')


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')


class MarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(child=serializers.CharField(), required=False)
    all = serializers.BooleanField(default=False)
