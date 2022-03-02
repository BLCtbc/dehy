from oscar.apps.basket.abstract_models import AbstractBasket
from django.db import models

class Basket(AbstractBasket):
	payment_intent_id = models.CharField(max_length=100, help_text='Payment Intent ID(Stripe)', blank=True, null=True)
	stripe_customer_id = models.CharField(max_length=100, help_text='Stripe Customer ID', blank=True, null=True)

from oscar.apps.basket.models import *