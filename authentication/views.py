from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import Token
from sentry_sdk import capture_exception
from authentication.serializers import LoginSerializer
from user.models import AllUsers


# Create your views here.
class AuthViewSet(ModelViewSet):
	serializer_class = LoginSerializer
	queryset = AllUsers.objects.all()

	def get_queryset(self):
		if self.action in ['login', 'new_password']:
			return AllUsers.objects.all()
		elif self.action in ['create', 'forgot_password']:
			return AllUsers.objects.all()

	@action(methods=['POST'], url_path='login', detail=False, serializer_class=LoginSerializer)
	def login(self, request):
		try:
			user = self.get_queryset().filter(email=request.data.get('email', None)).first()
			# Check if user exists
			if not user:
				return Response({'error': 'Invalid Login Crednetials. (Email issue) remove later'}, status.HTTP_400_BAD_REQUEST)
			# Check if password is correct
			if not user.check_password(request.data.get('password',None)):
				return Response({'error': 'Invalid Login Crednetials. (Password issue) remove later'}, status.HTTP_400_BAD_REQUEST)
			# Check if account has been verified
			if not user.verified:
				return Response({'error': 'Account not verifified. Check Mail(Resend verification link)'}, status.HTTP_400_BAD_REQUEST)
			payload = jwt_token(user)
			return Response({'access':payload['access'], 'refresh':payload['refresh']})
		except Exception as e:
			capture_exception(e)
			return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

def jwt_token(user):
	refresh = RefreshToken.for_user(user)
	payload = {
		'user_id': user.id,
		'refresh': str(refresh),
		'access': str(refresh.access_token),
	}

	token, _ = Token.objects.update_or_create(
			user=user, token_type='AUTH_TOKEN',
			defaults={'user': user, 'token':'jwt_token', 'token_type': 'AUTH_TOKEN', 'refresh': payload['refresh'], 'access': payload['access']})
	return payload
