from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'assessments', views.SkillAssessmentViewSet, basename='skillassessment')
router.register(r'recommendations', views.CareerRecommendationViewSet, basename='careerrecommendation')
router.register(r'trends', views.IndustryTrendViewSet, basename='industrytrend')
router.register(r'salaries', views.SalaryInsightViewSet, basename='salaryinsight')

urlpatterns = [
    path('', include(router.urls)),
]
