from rest_framework import serializers
from .models import Roadmap, Milestone, DailyPlan, Resource, CAREER_GOALS


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class DailyPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyPlan
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class RoadmapListSerializer(serializers.ModelSerializer):
    career_goal_display = serializers.CharField(source='get_career_goal_display', read_only=True)

    class Meta:
        model = Roadmap
        fields = ('id', 'title', 'career_goal', 'career_goal_display', 'duration_months',
                  'progress', 'is_active', 'is_completed', 'created_at', 'updated_at')


class RoadmapSerializer(serializers.ModelSerializer):
    milestone_set = MilestoneSerializer(many=True, read_only=True)
    resource_set = ResourceSerializer(many=True, read_only=True)
    career_goal_display = serializers.CharField(source='get_career_goal_display', read_only=True)

    class Meta:
        model = Roadmap
        fields = '__all__'
        read_only_fields = ('id', 'user', 'progress', 'is_completed', 'created_at', 'updated_at')


class GenerateRoadmapSerializer(serializers.Serializer):
    career_goal = serializers.ChoiceField(choices=[g[0] for g in CAREER_GOALS])
    duration_months = serializers.IntegerField(min_value=1, max_value=24, default=6)
    skill_level = serializers.ChoiceField(choices=['beginner', 'intermediate', 'advanced'], default='beginner')
    custom_goal = serializers.CharField(required=False, allow_blank=True)
