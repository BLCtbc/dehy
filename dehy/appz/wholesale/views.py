from django.shortcuts import render, redirect
from django.views import generic
from django.http import FileResponse
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_class, get_model
from django.contrib.sites.shortcuts import get_current_site
import os, requests
from django.conf import settings
from dehy.utils import quickbooks

WholesaleAccountCreationForm = get_class('dehy.appz.wholesale.forms', 'WholesaleAccountCreationForm')
# Create your views here.

class WholesaleView(generic.TemplateView):
	template_name = 'dehy/wholesale/wholesale.html'
	def get_context_data(self, *args, **kwargs):
		img_names = ['img/custom/dehy_cocktail_lemon_rough.jpeg', 'img/custom/dehy_strain_pouring.jpeg', 'img/custom/rose_cocktail_closeup.jpeg', 'img/custom/tall_pink_cocktail_lime_on_mirror.jpeg', 'img/custom/dehy_tiki_fire.jpeg', 'img/custom/dehy_cocktail_kiwi.jpeg']
		titles = ["Elevate & Refine","Reduce Labor","Reduce Waste","Increase Profits","Instagrammable & Inspirational","Increase Value"]
		descriptions = ["\nIt has never been so easy to bring the level of craft and style to your cocktail presentations that your guests have come to expect.\n","\nBy reducing the time spent preparing fresh fruit during service, you can trim labor costs and let your staff focus on what matters most: the guest experience.\n","\nDehydrated cocktail garnishes help you achieve your sustainability goals by reducing wasted produce and lowering your carbon footprint.\n","\nOur dehydrated garnishes are priced to fit into even the most aggressive cost-of-goods models.  We work to keep our prices stable even through the most volatile pricing periods for citrus and other fresh fruits. \n","\nHelp drive creative inspiration for your team with our ever growing selection of fruits and flowers and help create memorable moments that guests will want to share.  \n","\nConsistent, stunning garnishes showcase intention and care to your guests, enhancing their experience and providing a higher perceived value that leaves them with a greater satisfaction from their purchase. \n"]
		ctx = super().get_context_data(*args, **kwargs)
		ctx['card_list'] = []
		for d,t,img in zip(descriptions,titles, img_names):
			ctx['card_list'].append({'title':_(t), 'description':_(d), 'img':img})

		return ctx

class WholesaleRegisterView(generic.edit.FormView):
	template_name = 'dehy/wholesale/register.html'
	form_class = WholesaleAccountCreationForm

	def post(self, request, *args, **kwargs):
		response = super().post(request, *args, **kwargs)

	def form_valid(self, form):
		# form.create_customer()
		form.send_email(self.request)
		return super().form_valid(form)


def wholesale_pricing_pdf_view(request):
	file_path = os.path.join('static', 'pdf/dehy_wholesale_pricing_2022.pdf')
	response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
	return response

# def oauth(request):
#     auth_client = AuthClient(
#         quickbooks.api_key,
#         quickbooks.secret_key,
#         quickbooks.redirect_uri,
#         quickbooks.environment,
#     )
#
#     url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
#     request.session['state'] = auth_client.state_token
#     return redirect(url)
#
# def auth_code_handler(request):
# 	state = request.GET.get('state', None)
# 	error = request.GET.get('error', None)
#
# 	if error == 'access_denied':
# 		print('access denied')
# 		# return redirect('sampleAppOAuth2:index')
#
# 	if state is None:
# 		return HttpResponseBadRequest()
#
# 	elif state != get_CSRF_token(request):  # validate against CSRF attacks
# 		return HttpResponse('unauthorized', status=401)
#
# 	auth_code = request.GET.get('code', None)
# 	if auth_code is None:
# 		return HttpResponseBadRequest()
#
# 	bearer = quickbooks.get_bearer_token(auth_code)
# 	realm_id = request.GET.get('realm_id', None)
# 	quickbooks.update_session(request, bearer.access_token, bearer.refresh_token, realm_id)
#
# 	# Validate JWT tokens only for OpenID scope
# 	if bearer.id_token is not None:
# 		if not quickbooks.validate_jwt_token(bearer.id_token):
# 			return HttpResponse('JWT Validation failed. Please try signing in again.')
# 		else:
# 			return redirect('sampleAppOAuth2:connected')
# 	else:
# 		return redirect('sampleAppOAuth2:connected')