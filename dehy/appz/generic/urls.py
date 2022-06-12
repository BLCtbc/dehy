from django.urls import path, re_path
from . import views
from dehy.appz.customer import views as customer_views
from dehy.appz.checkout import views as checkout_views

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),
	path('returns-refunds/', views.ReturnsRefundsView.as_view(), name='returns'),
	path('faq/', views.FAQView.as_view(), name='faq'),
	path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
	path('contact/', views.contact_view, name='contact'),
	path('terms-of-service/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
	path('invoice/<int:pk>/', views.InvoiceView.as_view(), name='invoice'),
	path('ajax/get_cart_quantity/', views.get_cart_quantity, name='get_cart_quantity'),
	path('ajax/create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
	path('shipping/location/', checkout_views.ajax_get_shipping_methods, name='get_shipping_methods'),
	path('shipping/set_method/', checkout_views.ajax_set_shipping_method, name='set_shipping_method'),
	path('shipping/validate_address/', views.get_validated_address, name='validate_address'),
	path('webhooks/new_order_received/', views.shipstation_webhook_order_received, name='shipstation_webhook_order_received'),
	path('webhooks/order_submitted/', checkout_views.webhook_submit_order, name='webhook_submit_order'),
	path('webhooks/order_shipped/', views.shipstation_webhook_order_shipped, name='shipstation_webhook_order_shipped'),
	path('mailing_list/add', views.MailingListView.as_view(), name='add_user_to_mailing_list'),
	path('recaptcha_verify/', views.recaptcha_verify, name='recaptcha'),
	re_path(r'^recaptcha_verify\?token=(?P<token>[\w\-\d\_]+)', views.recaptcha_verify, name='recaptcha_verify'),
	path('accounts/billing/set-default/', customer_views.set_card_default, name='billing-set-card-default'),
	path('accounts/billing/remove-card/', customer_views.remove_user_card, name='billing-remove-user-card'),
	# path('accounts/verify/<uidb64>/<token>', customer_views.verify_account, name='verify_account')
]

