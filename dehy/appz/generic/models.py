from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.

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
	message = models.TextField(_("Message"), default="", help_text='message')
	first_name = models.CharField(_("First Name"), blank=True, null=True, max_length=50)
	last_name = models.CharField(_("Last Name"), blank=True, null=True, max_length=50)
	date_created = models.DateField(auto_now_add=True, editable=False)

	def __str__(self):
		return f"{self.email}, message: {self.message}, created: {self.date_created}"


class MessageUser(models.Model):
	email = models.EmailField(unique=True, help_text='Email Address')
	date_created = models.DateField(auto_now_add=True, editable=False)

	def __str__(self):
		return f"{self.email}"

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