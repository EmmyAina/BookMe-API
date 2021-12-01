from rest_framework import serializers
from .models import Bookings, BusinessOwner
from user.models import AllUsers
from rest_framework.exceptions import PermissionDenied

class RegisterBusinessSeriaizer(serializers.ModelSerializer):
	class Meta:
		model = BusinessOwner
		exclude = ('business_owner', 'verified')

	def create(self, validated_data):
		current_user = AllUsers.objects.filter(email=self.context['request'].user).first()
		if current_user.has_business_account:
			raise PermissionDenied('Business Account for this user already exists')
		if current_user.verified:
			validated_data['verified'] = True
		validated_data['business_owner'] = current_user
		business_instance = self.Meta.model(**validated_data)
		business_instance.save()
		current_user.business_account()
		return business_instance


class ListBusinessSeriaizer(serializers.ModelSerializer):
	class Meta:
		model = BusinessOwner
		exclude = ('business_owner', 'verified')

class MakeBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bookings
		exclude = ('client','approved')

	def create(self,validated_data):
		current_user = AllUsers.objects.filter(
			email=self.context['request'].user).first()
		validated_data['client'] = current_user
		booking_instance = self.Meta.model(**validated_data)
		booking_instance.save()
		return booking_instance


class ApproveBookingSerializer(serializers.Serializer):
	booking_id = serializers.CharField(required=True)
	status = serializers.BooleanField(default=False)

