from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views import generic
from oscar.core.loading import get_class, get_model

FAQ = get_model('generic', 'FAQ')

FAQCreateUpdateForm = get_class('dashboard.faq.forms', 'FAQCreateUpdateForm')
FAQSearchForm = get_class('dashboard.faq.forms', 'FAQSearchForm')

class FAQListView(generic.ListView):
	"""
	Dashboard view of the recipe list.
	Supports the permission-based dashboard.
	"""

	model = FAQ
	template_name = 'dehy/dashboard/faq/faq_list.html'
	context_object_name = "faq_list"
	context_table_name = 'faqs'
	paginate_by = 20
	filterform_class = FAQSearchForm
	form_class = FAQSearchForm


	def get_title(self):
		data = getattr(self.filterform, 'cleaned_data', {})
		name = data.get('name', None)
		ingredients = data.get('ingredients', None)
		if name and not ingredients:
			return gettext('Recipes matching "%s"') % (name)
		elif name and ingredients:
			return gettext('Recipes matching "%s" containing "%s"') % (name, ingredients)
		elif ingredients:
			return gettext('Recipes containing "%s"') % (ingredients)
		else:
			return gettext('Recipes')

	def get_context_data(self, **kwargs):
		data = super().get_context_data(**kwargs)
		data['filterform'] = self.filterform
		data['queryset_description'] = self.get_title()
		return data

	def get_queryset(self):
		qs = self.model.objects.all()
		self.filterform = self.filterform_class(self.request.GET)
		if self.filterform.is_valid():
			qs = self.filterform.apply_filters(qs)
		return qs

class FAQCreateView(generic.CreateView):
	model = FAQ
	template_name = 'dehy/dashboard/faq/faq_update.html'
	form_class = FAQCreateUpdateForm
	success_url = reverse_lazy('dashboard:faq-list')

	# def post(self, *args, **kwargs):
	# 	form = self.form_class(self.request.POST)
	# 	print(f'form.is_valid: {form.is_valid()}')
	#
	# 	# response = super().post(*args, **kwargs)
	# 	print(f'\n *** POST ')
	#
	# 	response = render(self.request, self.template_name, context=self.get_context_data())
	# 	return response

	def get_context_data(self, **kwargs):
		context_data = super().get_context_data(**kwargs)
		context_data['title'] = _('Create new FAQ')
		form = context_data['form']
		print(f'\n** VIEWS get_context_data: {context_data}')

		return context_data

	def forms_invalid(self, form, inlines):
		print(f'\n *** forms_invalid ')
		messages.error(self.request, "Your submitted data was not valid - please correct the below errors")
		return super().forms_invalid(form, inlines)

	def forms_valid(self, form, inlines):
		print(f'\n *** forms_valid ')
		response = super().forms_valid(form, inlines)
		msg = render_to_string('oscar/dashboard/faq/messages/faq_saved.html', {'faq': self.object})
		messages.success(self.request, msg, extra_tags='safe')
		return response

class FAQUpdateView(generic.UpdateView):
	model = FAQ
	template_name = "dehy/dashboard/faq/faq_update.html"
	form_class = FAQCreateUpdateForm
	success_url = reverse_lazy('dashboard:faq-list')


	def get_context_data(self, **kwargs):
		context_data = super().get_context_data(**kwargs)
		context_data['title'] = self.object.name
		print(f'\n** VIEWS get_context_data: {context_data}')

		return context_data

	def forms_invalid(self, form, inlines):
		messages.error(
			self.request,
			"Your submitted data was not valid - please correct the below errors")
		return super().forms_invalid(form, inlines)

	def forms_valid(self, form, inlines):
		msg = render_to_string('dehy/dashboard/faq/messages/faq_saved.html',
							   {'faq': self.object})
		messages.success(self.request, msg, extrforms_valida_tags='safe')
		return super().forms_valid(form, inlines)

class FAQDeleteView(generic.DeleteView):
	model = FAQ
	template_name = "dehy/dashboard/faq/faq_delete.html"
	success_url = reverse_lazy('dashboard:faq-list')