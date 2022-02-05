from django.db import models
from django.contrib.postgres.fields import ArrayField
from oscar.models.fields import AutoSlugField
# Create your models here.

class Recipe(models.Model):
	name = models.CharField(max_length=100, default="", help_text='Name of the recipe')
	description = models.TextField(help_text='A short introduction about the recipe, origin, summary, etc.', default="", blank=True, null=True)
	ingredients = ArrayField(
		ArrayField(base_field=models.CharField(max_length=50), size=3)
	)

	steps = ArrayField(models.CharField(max_length=300), default=list)
	slug = models.SlugField(max_length=50, unique=True, editable=True)
	date_created = models.DateField(auto_now_add=True, editable=False)
	last_modified = models.DateField(auto_now=True, editable=False)
	featured = models.BooleanField(default=False)
	# image = models.ImageField()

	class Meta:
		ordering = ['-date_created']

