from rest_framework import urlpatterns
from .views import UserViewset
from django.urls import path,include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', UserViewset)

urlpatterns = [
	path('', include(router.urls))
]