# Generated by Django 3.2.11 on 2022-03-01 18:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0014_rename_additional_info_questionaire_order_additional_info_questionnaire'),
        ('generic', '0007_auto_20220227_1722'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AdditionalInfoQuestionaire',
            new_name='AdditionalInfoQuestionnaire',
        ),
    ]
