from django.conf import settings
from django.http import Http404, HttpResponseForbidden
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.db.models import F, Q, Case, Max, When

from oscar.core.loading import get_class

ReportForm = get_class('dashboard.reports.forms', 'ReportForm')
GeneratorRepository = get_class('dashboard.reports.utils',
								'GeneratorRepository')


class IndexView(ListView):
	template_name = 'oscar/dashboard/reports/index.html'
	paginate_by = settings.OSCAR_DASHBOARD_ITEMS_PER_PAGE
	context_object_name = 'objects'
	report_form_class = ReportForm
	generator_repository = GeneratorRepository

	def _get_generator(self, form):
		code = form.cleaned_data['report_type']

		repo = self.generator_repository()
		generator_cls = repo.get_generator(code)
		if not generator_cls:
			raise Http404()

		download = form.cleaned_data['download']
		formatter = 'CSV' if download else 'HTML'

		return generator_cls(start_date=form.cleaned_data['date_from'],
							 end_date=form.cleaned_data['date_to'],
							 formatter=formatter)

	def get(self, request, *args, **kwargs):

		print(dir(request))
		print(request.path)
		print(request.get_host())
		print('request.scheme: ', request.scheme)
		print(request.resolver_match)

		if 'report_type' in request.GET:
			form = self.report_form_class(request.GET)
			if form.is_valid():
				generator = self._get_generator(form)
				if not generator.is_available_to(request.user):
					return HttpResponseForbidden(_("You do not have access to"
												   " this report"))

				report = generator.generate()

				if form.cleaned_data['download']:
					return report
				else:

					self.template_name = generator.filename()
					self.object_list = self.queryset = generator.queryset

					if 'product_analytics' in request.GET.get('report_type'):
						self.queryset = self.queryset.select_related('product__parent').prefetch_related('product__parent__stockrecords', 'product__stockrecords')
						self.queryset = self.queryset.filter(Q(product__structure='child') | Q(product__structure='standalone'))

						self.queryset = self.queryset.annotate(price=Case(
								When(product__structure='child', then=Max('product__stockrecords__price')),
								When(product__structure='standalone', then=Max('product__stockrecords__price')),
							)
						).annotate(total_revenue=F('price') * F('num_purchases'))


					if request.GET.get('sort'):
						trans_table = {'asc':'', 'desc':'-'}
						sort_direction = trans_table[request.GET.get('dir')] if request.GET.get('dir', None) else ''
						sorting = f"{sort_direction}{request.GET.get('sort')}"

						if request.GET.get('sort')=='product__title':
							sort_direction = trans_table[request.GET.get('dir')] if request.GET.get('dir', None) else ''
							sorting = f"{sort_direction}real_title"
							self.queryset = self.queryset.annotate(real_title=Case(
									When(product__structure='child', then=F('product__parent__title')),
									When(product__structure='standalone', then=F('product__title')),
								)
							).order_by(sorting, f'{sort_direction}price')



						else:
							self.queryset = self.queryset.order_by(sorting)



					context = self.get_context_data(object_list=self.queryset)
					context['form'] = form
					context['description'] = generator.report_description()
					return self.render_to_response(context)
		else:
			form = self.report_form_class()
		return TemplateResponse(request, self.template_name, {'form': form})