from django.db import models
from .models import AllUsers
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
	class Meta:
		model = AllUsers
		fields = ['id', 'email', 'first_name','last_name', 'gender', 'password',]
		extra_kwargs = {'password': {'write_only': True}}

	def create(self, validated_data):
		password = validated_data.pop('password', None)
		user_instance = self.Meta.model(**validated_data)

		if password != None:
			user_instance.set_password(password)
		user_instance.save()
		return user_instance
