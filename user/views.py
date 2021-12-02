from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from helpers import send_password_reset_token, send_verification_token
from authentication.models import TOKEN_TYPE, Token
from authentication.serializers import ChangePasswordSerializer, ForgotPasswordSerializer, NewPasswordSerializer, VerifyTokenSerializer
from .models import AllUsers
from .serializers import UserRegistrationSerializer
from sentry_sdk import capture_exception
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from authentication.models import Token
from django.utils.crypto import get_random_string

# Create your views here.


class UserViewset(ModelViewSet):
	serializer_class = UserRegistrationSerializer
	queryset = AllUsers.objects.all()
	permission_classes = [AllowAny,]
	filter_backends = [OrderingFilter, SearchFilter]

	def get_permissions(self):
		permission_classes = self.permission_classes
		if self.action in ['create', 'partial_update', 'get_participant']:
			permission_classes = [AllowAny]
		elif self.action in ['list', 'change_password']:
			permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]

	def get_queryset(self):
		if self.action in ['verify_account', 'new_password']:
			return Token.objects.all()
		elif self.action in ['register', 'forgot_password', 'change_password']:
			return AllUsers.objects.all()

	@action(methods=['POST'], url_path='register', detail=False, serializer_class=UserRegistrationSerializer)
	def register(self, request, *args, **kwargs):
		try:
			serializer = self.serializer_class(data=request.data)
			serializer.is_valid(raise_exception=True)
			serializer.save()
			return send_verification_token(
				self.get_queryset().filter(email=request.data['email']).first()
			)
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

	@action(methods=['POST'], url_path='verify-account', detail=False, serializer_class=VerifyTokenSerializer)
	def verify_account(self, request):
		try:
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid(raise_exception=True):
				token = self.get_queryset().filter(
					token=request.data.get('token', None)).first()
				if token and token.is_valid():
					token.verify_user()
					token.delete()

				# >>>>>> Login User After Verification
				return Response({
					'message': "Account Verified Successfully"
				})
			pass
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

	@action(methods=['POST'], url_path='forgot-password', detail=False, serializer_class=ForgotPasswordSerializer)
	def forgot_password(self, request):
		try:
			user = self.get_queryset().filter(email=request.data['email']).first()
			if not user:
				return Response({'error': "Invalid Email Address"})
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid(raise_exception=True):
				return send_password_reset_token(self.get_queryset().filter(email=request.data['email']).first())
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

	@action(methods=['POST'], url_path='new-password', detail=False, serializer_class=NewPasswordSerializer)
	def new_password(self, request):
		try:
			if request.data.get('password',None) != request.data.get('confirm_password', None):
				return Response({
					'error': 'Passwords do not match'
				})
			serializer = self.serializer_class(data=request.data)
			if serializer.is_valid(raise_exception=True):
				token = self.get_queryset().filter(token=request.data.get('token', None)).first()
				if token and token.is_valid(raise_exception=True):
					token.reset_user_password(password=request.data['password'])
					print(token)
					token.delete()
					return Response({
						"message": 'Password Reset Successfully'
					}, status.HTTP_200_OK)
				else:
					return Response({
						'error': 'Invalid Token, send reset mail again'
					})
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

	@action(methods=['POST'], url_path='change-password', detail=False, serializer_class=ChangePasswordSerializer)
	def change_password(self, request):
		try:
			serializer = self.serializer_class(data=request.data)
			user = self.get_queryset().filter(email=request.user).first()
			if serializer.is_valid(raise_exception=True):
				if request.data.get('new_password', None) != request.data.get('confirm_password', None):
					return Response({
						'error': 'Passwords do not match'
					})
				elif not user.check_password(request.data.get('old_password', None)):
					return Response({
						'error': 'Old password not correct'
					})
				user.change_password(password=request.data['new_password'])
				return Response({
                                    'message': 'Password Changed Successfully'
                                })
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
