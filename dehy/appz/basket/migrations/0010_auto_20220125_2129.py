# Generated by Django 3.2.11 on 2022-01-26 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0009_line_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basket',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='line',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='lineattribute',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
