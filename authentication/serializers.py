from rest_framework import serializers
from .models import Token

class VerifyTokenSerializer(serializers.Serializer):
	token = serializers.CharField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
	email = serializers.EmailField(required=True)

class NewPasswordSerializer(serializers.Serializer):
	token = serializers.CharField(required=True)
	password = serializers.CharField(required=True)
	confirm_password = serializers.CharField(required=True)
