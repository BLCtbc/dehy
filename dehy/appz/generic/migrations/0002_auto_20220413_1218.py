# Generated by Django 3.2.12 on 2022-04-13 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('generic', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='subject',
            field=models.CharField(blank=True, help_text='What is the nature if your inquiry?', max_length=50, null=True, verbose_name='Subject'),
        ),
        migrations.AlterField(
            model_name='message',
            name='message',
            field=models.TextField(default='', help_text='Your inquiry', verbose_name='Message'),
        ),
    ]
