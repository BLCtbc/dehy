# Generated by Django 3.2.12 on 2022-04-02 19:07

import dehy.appz.recipes.models
from django.db import migrations, models
import django_better_admin_arrayfield.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', help_text='Name of the recipe', max_length=100)),
                ('description', models.TextField(blank=True, default='', help_text='A short introduction about the recipe, origin, summary, etc.', null=True)),
                ('ingredients', django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(max_length=150), default=list, help_text='Ingredient list', size=None)),
                ('steps', django_better_admin_arrayfield.models.fields.ArrayField(base_field=models.CharField(max_length=300), default=list, help_text='Directions list', size=None, verbose_name='Directions')),
                ('slug', models.SlugField(unique=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_modified', models.DateField(auto_now=True)),
                ('featured', models.BooleanField(default=False, help_text='Feature this recipe on the homepage?')),
                ('image', models.ImageField(blank=True, upload_to=dehy.appz.recipes.models.upload_to_slug)),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
    ]
