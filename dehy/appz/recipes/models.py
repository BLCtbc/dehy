from django.db import models
from django.contrib.postgres.fields import ArrayField
from oscar.models.fields import AutoSlugField
from django_better_admin_arrayfield.models import fields as dbaa

# Create your models here.
def upload_to_slug(instance, filename):
	return f"images/recipes/{instance.slug}/{filename}"

class Recipe(models.Model):
	name = models.CharField(max_length=100, default="", help_text='Name of the recipe')
	description = models.TextField(help_text='A short introduction about the recipe, origin, summary, etc.', default="", blank=True, null=True)
	ingredients = dbaa.ArrayField(models.CharField(max_length=150), default=list, help_text='Ingredient list')

	steps = dbaa.ArrayField(models.CharField(max_length=300), default=list, help_text='Directions list', verbose_name='Directions')
	slug = models.SlugField(max_length=50, unique=True, editable=True)
	date_created = models.DateField(auto_now_add=True, editable=False)
	last_modified = models.DateField(auto_now=True, editable=False)
	featured = models.BooleanField(default=False, help_text='Feature this recipe on the homepage?')
	image = models.ImageField(upload_to=upload_to_slug, blank=True)

	class Meta:
		ordering = ['-date_created']

	def __str__(self):
		return f"{self.name}, Date created: {self.date_created}, Last edited: {self.last_modified}"


