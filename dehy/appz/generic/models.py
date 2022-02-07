from django.db import models

# Create your models here.

class QandA(models.Model):
	"""
	A question and an answer to be used in the FAQ page.
	"""

	question = models.TextField(max_length=500, default="", help_text='The frequently asked question text')
	answer = models.TextField(max_length=500, blank=True, null=True, help_text='The answer to the question')

	date_created = models.DateField(auto_now_add=True, editable=False)
	last_modified = models.DateField(auto_now=True, editable=False)

class VisionStatement(models.Model):
	title = models.CharField(max_length=50, default="", help_text='Vision name')
	description = models.TextField(default="", help_text='Description')
	date_created = models.DateField(auto_now_add=True, editable=False)
	last_modified = models.DateField(auto_now=True, editable=False)

	def __str__(self):
		return f"{self.title}, created: {self.date_created}, modified: {self.last_modified}"