# Generated by Django 3.2.12 on 2022-03-30 21:04

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_rename_additional_info_questionaire_order_additional_info_questionnaire'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingaddress',
            name='phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None, verbose_name='Phone number'),
        ),
    ]
