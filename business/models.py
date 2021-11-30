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
	date_joined = models.DateTimeField(auto_now_add=True, null=True)

	def __str__(self):
		return f'{self.business_name} {self.business_owner.email}'