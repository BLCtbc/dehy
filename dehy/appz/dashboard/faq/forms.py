from django import forms
import math
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_model
from django.core.validators import RegexValidator
from django.contrib.postgres.forms import SimpleArrayField, SplitArrayField
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from django_better_admin_arrayfield.forms.widgets import DynamicArrayTextareaWidget
from django_better_admin_arrayfield.forms.fields import DynamicArrayField


FAQ = get_model('generic', 'FAQ')

class FAQSearchForm(forms.Form):

	question = forms.CharField(label=_('FAQ question'), required=False)
	answer = forms.CharField(label=_('FAQ answer'), required=False)

	def is_empty(self):
		d = getattr(self, 'cleaned_data', {})
		def empty(key): return not d.get(key, None)
		return empty('question') and empty('answer')

	def apply_question_filter(self, qs, value):
		words = value.replace(',', ' ').split()
		q = [Q(city__icontains=word) for word in words]
		return qs.filter(*q)

	def apply_answer_filter(self, qs, value):
		return qs.filter(answer__icontains=value)

	def apply_filters(self, qs):
		for key, value in self.cleaned_data.items():
			if value:
				qs = getattr(self, 'apply_%s_filter' % key)(qs, value)
		return qs


class FAQCreateUpdateForm(forms.ModelForm):

	class Meta:
		model = FAQ
		fields = ['question', 'answer']

