from django.db.models import query
from django.shortcuts import render
from rest_framework import status
from rest_framework.utils import serializer_helpers
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from authentication.models import TOKEN_TYPE, Token
from authentication.serializers import ForgotPasswordSerializer, NewPasswordSerializer, VerifyTokenSerializer
from .models import AllUsers
from .serializers import UserRegistrationSerializer
from sentry_sdk import capture_exception
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
# from django_filters.rest_framework import DjangoFilterBackend
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
		elif self.action == 'list':
			permission_classes = [IsAuthenticated, IsAdminUser]
		return [permission() for permission in permission_classes]

	def get_queryset(self):
		if self.action in ['verify_token', 'new_password']:
			return Token.objects.all()
		elif self.action in ['create', 'forgot_password']:
			return AllUsers.objects.all()

	@action(methods=['POST'], url_path='register', detail=False, serializer_class=UserRegistrationSerializer)
	def register(self, request, *args, **kwargs):
		try:
			serializer = self.serializer_class(data=request.data)
			serializer.is_valid(raise_exception=True)
			serializer.save()

			# >>> Send Verification Email

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
				if token and token.is_valid(raise_exception=True):
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



def send_verification_token(user):
	try:
		token, _ = Token.objects.update_or_create(
			user=user, token_type='ACCOUNT_VERIFICATION',
			defaults={'user': user, 'token_type': 'ACCOUNT_VERIFICATION', 'token': get_random_string(120)})
		print(token)

		return Response({
			'message': 'Verification Mail Sent Successfully'
		}, status=status.HTTP_200_OK)
	except Exception as e:
		capture_exception(e)
		return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_password_reset_token(user):
	try:
		token, _ = Token.objects.update_or_create(
			user=user, token_type='PASSWORD_RESET',
			defaults={'user': user, 'token_type': 'PASSWORD_RESET', 'token': get_random_string(120)})
		print(token)

		return Response({
			'message': 'Password Reset Sent Successfully'
		}, status=status.HTTP_200_OK)
	except Exception as e:
		capture_exception(e)
		return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
