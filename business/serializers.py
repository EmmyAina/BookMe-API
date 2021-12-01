from rest_framework import serializers
from .models import BusinessOwner
from user.models import AllUsers
from rest_framework.exceptions import PermissionDenied

class RegisterBusinessSeriaizer(serializers.ModelSerializer):
	class Meta:
		model = BusinessOwner
		exclude = ('business_owner',)

	def create(self, validated_data):
		current_user = AllUsers.objects.filter(email=self.context['request'].user).first()
		if current_user.has_business_account:
			raise PermissionDenied('Business Account for this user already exists')
		validated_data['business_owner'] = current_user
		business_instance = self.Meta.model(**validated_data)
		business_instance.save()
		current_user.business_account()
		return business_instance
