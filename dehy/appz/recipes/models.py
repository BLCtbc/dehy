from django.db import models
from django.contrib.postgres.fields import ArrayField
from oscar.models.fields import AutoSlugField
# Create your models here.

class Recipe(models.Model):
	name = models.CharField(max_length=100, default="", help_text='Name of the recipe')
	description = models.TextField(help_text='A short introduction about the recipe, origin, summary, etc.')
	ingredients = ArrayField(models.CharField(max_length=50))
	slug = AutoSlugField(max_length=50, unique=True, populate_from=name, editable=True)
	date_created = models.DateField(auto_now_add=True, editable=False)
	last_modified = models.DateField(auto_now=True, editable=False)

