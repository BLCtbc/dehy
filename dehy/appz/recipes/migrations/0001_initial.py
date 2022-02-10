# Generated by Django 3.2.11 on 2022-02-02 04:17

import django.contrib.postgres.fields
from django.db import migrations, models
import oscar.models.fields.autoslugfield


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
                ('description', models.TextField(help_text='A short introduction about the recipe, origin, summary, etc.')),
                ('ingredients', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), size=None)),
                ('slug', oscar.models.fields.autoslugfield.AutoSlugField(blank=True, editable=False, populate_from=models.CharField(default='', help_text='Name of the recipe', max_length=100), unique=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('last_modified', models.DateField(auto_now=True)),
            ],
        ),
    ]
