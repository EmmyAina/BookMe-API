from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import AbstractBaseUser, Permission, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _
import uuid

from .manager import UserManager

GENDER = (
	('Male', 'Male'),
	('Female', 'Female'),
	('Others', 'Others'),
)

AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}


class AllUsers(AbstractBaseUser, PermissionsMixin):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	email = models.EmailField(
		_('email address'), null=True, blank=False, unique=True)
	first_name = models.CharField(max_length=255, blank=False)
	last_name = models.CharField(max_length=255, blank=False)
	password = models.CharField(max_length=255, null=True)
	gender = models.CharField(max_length=50, choices=GENDER, blank=True)
	is_staff = models.BooleanField(default=False)
	has_business_account = models.BooleanField(default=False)
	date_joined = models.DateTimeField(auto_now_add=True, null=True)
	verified = models.BooleanField(default=False)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	class Meta:
		ordering = ('-date_joined',)

	objects = UserManager()

	def __str__(self):
		return self.email
