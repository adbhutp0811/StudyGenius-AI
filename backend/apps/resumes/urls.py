from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.ResumeTemplateViewSet, basename='resume-template')
router.register(r'', views.ResumeViewSet, basename='resume')

urlpatterns = [
    path('', include(router.urls)),
]
