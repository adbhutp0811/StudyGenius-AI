from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'milestones', views.MilestoneViewSet, basename='milestone')
router.register(r'resources', views.ResourceViewSet, basename='resource')
router.register(r'', views.RoadmapViewSet, basename='roadmap')

urlpatterns = [
    path('', include(router.urls)),
]
