from django.shortcuts import render
from django.views import generic
from django.utils.translation import gettext_lazy as _
from oscar.core.loading import get_class, get_model
from django.contrib.sites.shortcuts import get_current_site

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


