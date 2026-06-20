from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'subjects', views.SubjectViewSet, basename='subject')
router.register(r'papers', views.QuestionPaperViewSet, basename='questionpaper')
router.register(r'bank', views.QuestionBankViewSet, basename='questionbank')

urlpatterns = [
    path('', include(router.urls)),
]
