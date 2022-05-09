from django.urls import path, re_path
from . import views
from dehy.appz.checkout.views import ajax_get_shipping_methods, ajax_set_shipping_method, webhook_submit_order

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),
	path('returns-refunds/', views.ReturnsRefundsView.as_view(), name='returns'),
	path('wholesale/', views.WholesaleView.as_view(), name='wholesale'),
	path('faq/', views.FAQView.as_view(), name='faq'),
	path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
	path('contact/', views.contact_view, name='contact'),
	path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
	path('ajax/get_cart_quantity/', views.get_cart_quantity, name='get_cart_quantity'),
	path('ajax/create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
	path('shipping/location/', ajax_get_shipping_methods, name='get_shipping_methods'),
	path('shipping/set_method/', ajax_set_shipping_method, name='set_shipping_method'),
	path('webhooks/order_submitted/', webhook_submit_order, name='webhook_submit_order'),
	path('mailing_list/add', views.MailingListView.as_view(), name='add_user_to_mailing_list'),
	# path('recaptcha_verify/', views.recaptcha_verify, name='recaptcha'),
	re_path(r'^recaptcha_verify/?token=(?P<token>[\w\-\d\_]+)', views.recaptcha_verify, name='recaptcha_verify'),
]

