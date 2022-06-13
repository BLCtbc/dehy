from django.urls import path, re_path
from . import views
app_name = 'wholesale'

urlpatterns = [
	path('', views.WholesaleView.as_view(), name='index'),
	path('accountsetup/', views.WholesaleRegisterView.as_view(), name='register'),
	# path('qb/oauth2/'),
	# path('quickbooks/oauth2/'),
]

