# Generated by Django 3.2.11 on 2022-02-03 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_steps'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='featured',
            field=models.BooleanField(default=False),
        ),
    ]
