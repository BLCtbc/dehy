from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from oscar.apps.customer.abstract_models import AbstractUser

import datetime

class User(AbstractUser):
	stripe_customer_id = models.CharField(_('Stripe Customer ID'), max_length=255, blank=True)
	is_email_verified = models.BooleanField(default=False)
	receive_new_order_notifications = models.BooleanField(default=False)
	subscribed_to_mailing_list = models.BooleanField(_('Subscribed to our mailing list'), default=False, help_text=_('Check this option to receive updates about upcoming events, product availability, and exclusive offers.'))

	class Meta:
		permissions = [
            ("can_receive_new_order_notifications", "Gives the user permission to receive notification emails anytime a new order is placed."),
        ]

class FedexAuthToken(models.Model):
	access_token = models.CharField(_("Token"), max_length=2000, default="")
	expires_in = models.IntegerField(_("Expires in"), default=0, help_text=_("Seconds"))
	date_created = models.DateTimeField(auto_now=True, editable=False)
	scope = models.CharField(_("Scope"), max_length=20, default="")

	def __str__(self):
		return f"Token: {self.access_token}, created: {self.date_created}"

	@property
	def expiration(self):
		return self.date_created + datetime.timedelta(seconds=self.expires_in)

	@property
	def expired(self):
		return datetime.datetime.now().astimezone() > self.expiration

	def save(self, *args, **kwargs):
		if not self.pk and FedexAuthToken.objects.exists():
			raise ValidationError('There is can be only one FedexAuthToken instance')

		return super().save(*args, **kwargs)


class FAQ(models.Model):
	"""
	A question and an answer to be used in the FAQ page.
	"""

	question = models.TextField(max_length=500, default="", help_text='The frequently asked question text')
	answer = models.TextField(max_length=500, blank=True, null=True, help_text='The answer to the question')

	date_created = models.DateField(auto_now_add=True, editable=False)
	last_modified = models.DateField(auto_now=True, editable=False)

class VisionStatement(models.Model):
	title = models.CharField(_("Title"), max_length=50, default="", help_text='Vision name')
	description = models.TextField(_("description"), default="", help_text='Description')
	date_created = models.DateField(auto_now_add=True, editable=False)
	last_modified = models.DateField(auto_now=True, editable=False)

	def __str__(self):
		return f"{self.title}, created: {self.date_created}, modified: {self.last_modified}"

class Message(models.Model):
	email = models.ForeignKey('MessageUser', on_delete=models.CASCADE)
	message = models.TextField(_("Message"), default="", help_text=_('Your inquiry'))
	subject = models.CharField(_('Subject'), blank=True, null=True, help_text=_("What is the nature if your inquiry?"), max_length=50)
	first_name = models.CharField(_("First Name"), blank=True, null=True, max_length=50)
	last_name = models.CharField(_("Last Name"), blank=True, null=True, max_length=50)
	date_created = models.DateTimeField(auto_now_add=True, editable=False)

	def __str__(self):
		return f"{self.email}, message: {self.message}, created: {self.date_created}"

# doubles as model for keeping track of user's subscribed to mailing list
class MessageUser(models.Model):
	email = models.EmailField(unique=True, help_text='Email Address')
	date_created = models.DateField(auto_now_add=True, editable=False)
	subscribed = models.BooleanField(default=True)

	def __str__(self):
		return f"{self.email}"

	@property
	def address(self):
		return self.email

class AdditionalInfoQuestionnaire(models.Model):
	BAR_OR_RESTAURANT,HOME,OTHER = 'b_r','h','o'
	CHOICES = [
		(BAR_OR_RESTAURANT, 'Bar or Restaurant'),
		(HOME, 'Home'),
		(OTHER, 'Other')
	]
	purchase_business_type = models.CharField(_("Business or Home"), choices=CHOICES, default=BAR_OR_RESTAURANT, max_length=3, help_text="Is this for home or commercial use?")
	business_name = models.CharField(max_length=100, help_text="What is the name of your Bar/Restaurant/Business?")
	date_created = models.DateField(auto_now_add=True, editable=False)

	# need a way of identifying who took the questionaire, ie. record user email, username, etc.
	# email = models.EmailField(unique=True, help_text='Email Address')