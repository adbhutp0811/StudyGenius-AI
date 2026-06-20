from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'bookmarks', views.BookmarkedAnswerViewSet, basename='bookmark')
router.register(r'', views.ChatSessionViewSet, basename='chatsession')

urlpatterns = [
    path('', include(router.urls)),
]
