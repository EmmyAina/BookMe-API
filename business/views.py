from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework import status
from rest_framework.serializers import Serializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import Bookings, BusinessOwner
from .serializers import ApproveBookingSerializer, ListBusinessSeriaizer, MakeBookingSerializer, RegisterBusinessSeriaizer
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
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
	def get_queryset(self):
		if self.action in ['approve_booking', 'make_booking']:
			return Bookings.objects.all()
		elif self.action in ['list']:
			return BusinessOwner.objects.all()

	def get_serializer_class(self):
		if self.action == 'create':
			return RegisterBusinessSeriaizer
		elif self.action == 'make_booking':
			return MakeBookingSerializer
		elif self.action == 'list':
			return ListBusinessSeriaizer
		elif self.action == 'approve_booking':
			return ApproveBookingSerializer

	def get_permissions(self):
		permission_classes = self.permission_classes
		if self.action in ['', 'initialize_reset', 'verify_token', 'retrieve', 'list']:
			permission_classes = [AllowAny]
		elif self.action in ['destroy', 'partial_update', 'create', 'make_booking', 'approve_booking']:
			permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]
		# if self.action == 'register_business':
		# 	return RegisterBusinessSeriaizer
	# @action(methods=['POST', 'GET'], url_path='register-business', detail=False)

	def create(self, request):
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

	def list(self, request):
		try:
			serializer = self.get_serializer(self.get_queryset(), many=True)
			return Response(serializer.data)
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated], url_path="student")
    # def get_participant(self, request):
    #     serializer_class = StudentInfoSerializer
    #     serialized_data = serializer_class(self.get_queryset(), many=True)
    #     if serialized_data.data:
    #         data = serialized_data.data[0]
    #         data['all_uploaded'] = check_all_certificates_uploaded(data)
    #         return Response(data)
    #     else:
    #         return Response(serialized_data.data)

	@action(methods=['POST'], url_path='make-booking', detail=False, serializer_class=MakeBookingSerializer)
	def make_booking(self, request):
		try:
			serializer = self.get_serializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			if self.get_queryset().filter(client=self.request.user).filter(time=request.data['time']).exists():
				return Response({
								'message': 'You already have a booking for this time',
							}, status.HTTP_406_NOT_ACCEPTABLE)
			elif self.get_queryset().filter(business=request.data['business']).filter(time=request.data['time']).exists():
				return Response({
								'message': 'This business already has a booking for this time',
							}, status.HTTP_406_NOT_ACCEPTABLE)
			serializer.save()
			return Response({
				'message': 'Booking Placed successfully!, Awaiting approval from business owner',
				'data': serializer.data
			}, status.HTTP_200_OK)
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

	@action(methods=['POST'], url_path='approve-booking', detail=False, serializer_class=ApproveBookingSerializer)
	def approve_booking(self, request):
		try:
			serializer = self.get_serializer(data=request.data)
			if serializer.is_valid(raise_exception=True):
				if request.data['status']:
					booking = self.get_queryset().filter(
						id=request.data.get('booking_id', None)).first()
					booking.add_booking()

					return Response({
						'message': 'Booking Approved',
						# 'data':serializer.validated_data
					}, status.HTTP_200_OK)
				else:
					return Response({
						'message': 'Booking Rejected',
						# 'data':serializer.validated_data
					}, status.HTTP_200_OK)
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
