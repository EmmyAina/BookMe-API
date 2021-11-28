from django.urls import include, path
from rest_framework import urlpatterns
from .views import AuthViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', AuthViewSet)

urlpatterns = [
	path('', include(router.urls))
]