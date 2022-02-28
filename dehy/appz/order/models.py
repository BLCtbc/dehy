from oscar.apps.order.abstract_models import AbstractOrder
from django.db import models

class Order(AbstractOrder):
	additional_info_questionaire = models.ForeignKey('generic.AdditionalInfoQuestionaire',
		on_delete=models.SET_NULL, null=True, blank=True)

from oscar.apps.order.models import *  # noqa isort:skip
