# Generated by Django 3.2.12 on 2022-04-02 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basket', '0009_line_date_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='payment_intent_client_secret',
            field=models.CharField(blank=True, help_text='Payment Intent Client Secret (Stripe)', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='basket',
            name='payment_intent_id',
            field=models.CharField(blank=True, help_text='Payment Intent ID(Stripe)', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='basket',
            name='stripe_customer_id',
            field=models.CharField(blank=True, help_text='Stripe Customer ID', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='basket',
            name='stripe_order_client_secret',
            field=models.CharField(blank=True, help_text='Order Client Secret (Stripe)', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='basket',
            name='stripe_order_id',
            field=models.CharField(blank=True, help_text='Stripe Order ID', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='basket',
            name='stripe_order_status',
            field=models.CharField(blank=True, help_text='Stripe Order Status', max_length=50, null=True),
        ),
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
