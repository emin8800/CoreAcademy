from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'content', ContentViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'homeworks', StudentWorkViewSet)
router.register("events", EventViewSet, basename="events")
router.register(r"materials-download", MaterialDownloadViewSet, basename="materials-download")
router.register(r'contact-messages', ContactMessageViewSet)

urlpatterns = [
    
    path('', include(router.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)