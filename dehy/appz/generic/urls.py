from django.urls import path
from . import views

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),
	path('custom/', views.CustomView.as_view(), name='custom'),
	path('returns/', views.ReturnsRefundsView.as_view(), name='returns'),
	path('wholesale/', views.WholesaleView.as_view(), name='wholesale'),
	path('contact/', views.ContactView.as_view(), name='contact'),
	path('faq/', views.FAQView.as_view(), name='faq'),
	path('ajax/get_cart_quantity/', views.get_cart_quantity, name='get_cart_quantity'),

]

