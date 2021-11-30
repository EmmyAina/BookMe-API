from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import BusinessOwner
from .serializers import RegisterBusinessSeriaizer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from sentry_sdk import capture_exception
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.generics import GenericAPIView


# Create your views here.
class BusinessViewSet(ModelViewSet):
    serializer_class = RegisterBusinessSeriaizer
    queryset = BusinessOwner.objects.all()
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['business_name', 'owner_full_name', ]

    # permission_classes = (IsAuthenticatedOrReadOnly, IsAuthenticated)
    # parser_classes = (FormParser, MultiPartParser)

    @action(methods=['POST'], url_path='register-business', detail=False, serializer_class=RegisterBusinessSeriaizer)
    def register_business(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'message': 'Business Account Created Successfully',
            }, status.HTTP_200_OK)
        except Exception as e:
            capture_exception(e)
            return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
