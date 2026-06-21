from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def root_view(request):
    return JsonResponse({
        'message': 'StudyGenius AI API is running',
        'docs': request.build_absolute_uri('/api/docs/'),
        'schema': request.build_absolute_uri('/api/schema/'),
    })


urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/resumes/', include('apps.resumes.urls')),
    path('api/roadmaps/', include('apps.roadmaps.urls')),
    path('api/doubts/', include('apps.doubts.urls')),
    path('api/blogs/', include('apps.blogs.urls')),
    path('api/youtube/', include('apps.youtube.urls')),
    path('api/pdfchat/', include('apps.pdfchat.urls')),
    path('api/career/', include('apps.career.urls')),
    path('api/question-papers/', include('apps.questionpapers.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
