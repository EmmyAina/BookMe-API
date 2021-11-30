from rest_framework import urlpatterns
from .views import BusinessViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', BusinessViewSet)

urlpatterns = [
	path('', include(router.urls))
]
