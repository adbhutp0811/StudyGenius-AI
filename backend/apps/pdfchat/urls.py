from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.PDFDocumentViewSet, basename='pdfdocument')
router.register(r'sessions', views.PDFChatSessionViewSet, basename='pdfchatsession')
router.register(r'highlights', views.DocumentHighlightViewSet, basename='documenthighlight')

urlpatterns = [
    path('', include(router.urls)),
]
