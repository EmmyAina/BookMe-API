from django.utils.crypto import get_random_string
from authentication.models import Token
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status
from sentry_sdk import capture_exception

def send_verification_token(user):
	try:
		token, _ = Token.objects.update_or_create(
			user=user, token_type='ACCOUNT_VERIFICATION',
			defaults={'user': user, 'token_type': 'ACCOUNT_VERIFICATION', 'token': get_random_string(120)})
		send_mail(
			'Account Verification',
			f'Use the link below to reset your account password. token {token.token} ',
			'from@example.com',
			[f'{token.user.email}'],
			fail_silently=False,
		)
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

		send_mail(
			'Password Reset',
			f'Use the link below to reset your account password. token {token.token} ',
			'from@example.com',
			[f'{token.user.email}'],
			fail_silently=False,
		)
		return Response({
			'message': 'Password Reset Sent Successfully'
		}, status=status.HTTP_200_OK)
	except Exception as e:
		capture_exception(e)
		return Response({'error': str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
