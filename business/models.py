from django.db import models
from django.db.models.base import Model
import uuid
# Create your models here.


class BusinessOwner(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	business_owner = models.ForeignKey('user.AllUsers', on_delete=models.CASCADE, null=True,
									related_name='business_owner')
	business_name = models.CharField(max_length=255, blank=False)
	owner_full_name = models.CharField(max_length=255, blank=False)
	address = models.TextField(max_length=255, null=True)
	phone_number = models.CharField(max_length=255, blank=False)
	verified = models.BooleanField(default=False)
	opening_time = models.TimeField()
	closing_time = models.TimeField()
	secondary_email = models.CharField(max_length=255, blank=False)
	booking_count = models.IntegerField(default=0)
	date_joined = models.DateTimeField(auto_now_add=True, null=True)

	def __str__(self):
		return f'{self.business_name} {self.business_owner.email}'

class Bookings(models.Model):
	client = models.ForeignKey(
		    'user.AllUsers', related_name='client', on_delete=models.CASCADE)
	business = models.ForeignKey(BusinessOwner,on_delete=models.CASCADE,related_name='service_provider',null=True,blank=True)
	time = models.DateTimeField()
	approved = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.business.business_name} was booked by {self.client.email} for {self.time}'

	def add_booking(self):
		self.approved = True
		self.save(update_fields=['approved'])
		self.business.booking_count+=1
		self.business.save(update_fields=['booking_count'])
