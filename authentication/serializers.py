from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

class VerifyTokenSerializer(serializers.Serializer):
	token = serializers.CharField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
	email = serializers.EmailField(required=True)

class NewPasswordSerializer(serializers.Serializer):
	token = serializers.CharField(required=True)
	password = serializers.CharField(required=True)
	confirm_password = serializers.CharField(required=True)


def required(value):
    if value is None:
        raise serializers.ValidationError('This field is required')


class LoginSerializer(serializers.Serializer):
	email = serializers.CharField(
		max_length=255, validators=[required])
	password = serializers.CharField(
		validators=[required],
		label=_("Password"),
		style={'input_type': 'password'},
		max_length=128,
		write_only=False
	)
