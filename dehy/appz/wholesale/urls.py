from django.urls import path, re_path
from . import views
app_name = 'wholesale'

urlpatterns = [
	path('', views.WholesaleView.as_view(), name='index'),
	path('accountsetup/', views.WholesaleRegisterView.as_view(), name='register'),
	path('pricing/', views.wholesale_pricing_pdf_view, name='pricing')
	# path('qb/oauth2/', views.oauth, name='oauth'),
	# path('quickbooks/oauth2/', views.oauth),
]

