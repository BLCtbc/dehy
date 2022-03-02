from oscar.apps.order.abstract_models import AbstractOrder
from django.db import models

class Order(AbstractOrder):
	additional_info_questionnaire = models.ForeignKey('generic.AdditionalInfoQuestionnaire',
		on_delete=models.SET_NULL, null=True, blank=True)

from oscar.apps.order.models import *  # noqa isort:skip
