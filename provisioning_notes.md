# Provisioning notes, how-to's, etc. for a custom django-oscar deployment

1. [installation and setup](#installation)
2. [providing initial data via data migration](#initial_data)
3. [customizing oscar](#customizing_oscar)
	- [adding field to existing Product](#edit_product_model)
	- [customizing/editing an existing oscar view](#edit_views)
	- [customizing an existing oscar template](#customising_template)
	- [change default currency](#default_currency)
	- [getting images to show](#fix_images)
	- [customizing dashboard forms](#dashboard_form_edit)
	- [modifying urls by overriding the default oscar app](#modify_urls)
	- [disabling a built-in oscar feature](#disable_feature)
	- [changing the oscar homepage](#edit_homepage)
4. [implementing paypal payment support with django-oscar-payapl](#django_oscar_paypal)
7. [git commands](#git_commands)
8. [linux cli commands](#server_cli)
---

Note, any changes made to `settings.py` might require restarting the server in order to take affect

1. ##### <a name="installation"></a> Creating new django project with [oscar-django](https://django-oscar.readthedocs.io/en/3.1/internals/getting_started.html#install-oscar-and-its-dependencies)

	- install dependencies + virtual env setup
		```sh
		$ git clone git@github.com:BLCtbc/dehy.git
		$ python3.7 -m venv venv # create the virtual environment
		$ source venv/bin/activate # activate the virtual environment
		$ export PROJECT_NAME=dehy && export APP_FOLDER=apps
		$ (venv) pip install --upgrade pip
		$ (venv) pip install 'django-oscar[sorl-thumbnail]' # should also install django and various other requirements
		$ (venv) pip install pycountry # additional dependency
		$ (venv) pip install psycopg2-binary # PostgreSQL requirement
		$ (venv) django-admin startproject $PROJECT_NAME # rename to w/e your project name is
		$ (venv) mv $PROJECT_NAME temp && mv temp/manage.py manage.py && mv temp/$PROJECT_NAME $PROJECT_NAME && rm -r temp
		```

	- add oscar-specific settings to `settings.py`

		changes to `settings.py` from [django-oscar documentation](https://django-oscar.readthedocs.io/en/3.1/internals/getting_started.html#django-settings)

		- add `from oscar.defaults import *` to the top of `settings.py`

		- add oscar's context processors to `settings.py`:

			```py
			'oscar.apps.search.context_processors.search_form',
			'oscar.apps.checkout.context_processors.checkout',
			'oscar.apps.communication.notifications.context_processors.notifications',
			'oscar.core.context_processors.metadata',
			```

		- add `SITE_ID = 1` and change `INSTALLED_APPS` to the following:
			```py
			# $PROJECT_NAME/settings.py
			...

			INSTALLED_APPS = [
			    'django.contrib.admin',
			    'django.contrib.auth',
			    'django.contrib.contenttypes',
			    'django.contrib.sessions',
			    'django.contrib.messages',
			    'django.contrib.staticfiles',

			    'django.contrib.sites',
			    'django.contrib.flatpages',

			    'oscar.config.Shop',
			    'oscar.apps.analytics.apps.AnalyticsConfig',
			    'oscar.apps.checkout.apps.CheckoutConfig',
			    'oscar.apps.address.apps.AddressConfig',
			    'oscar.apps.shipping.apps.ShippingConfig',
			    'oscar.apps.catalogue.apps.CatalogueConfig',
			    'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
			    'oscar.apps.communication.apps.CommunicationConfig',
			    'oscar.apps.partner.apps.PartnerConfig',
			    'oscar.apps.basket.apps.BasketConfig',
			    'oscar.apps.payment.apps.PaymentConfig',
			    'oscar.apps.offer.apps.OfferConfig',
			    'oscar.apps.order.apps.OrderConfig',
			    'oscar.apps.customer.apps.CustomerConfig',
			    'oscar.apps.search.apps.SearchConfig',
			    'oscar.apps.voucher.apps.VoucherConfig',
			    'oscar.apps.wishlists.apps.WishlistsConfig',
			    'oscar.apps.dashboard.apps.DashboardConfig',
			    'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
			    'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
			    'oscar.apps.dashboard.orders.apps.OrdersDashboardConfig',
			    'oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
			    'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
			    'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
			    'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
			    'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
			    'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
			    'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
			    'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
			    'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',

			    # 3rd-party apps that oscar depends on
			    'widget_tweaks',
			    'haystack',
			    'treebeard',
			    'sorl.thumbnail',   # Default thumbnail backend, can be replaced
			    'django_tables2',
			]

			SITE_ID = 1
			...
			```

		- update middleware in `settings.py`:
			```py
			MIDDLEWARE = [
		    	...
		    	'oscar.apps.basket.middleware.BasketMiddleware',
		    	'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
			]
			```
		- add authentication backends to `settings.py`:
			```py
			AUTHENTICATION_BACKENDS = [
			    'oscar.apps.customer.auth_backends.EmailBackend',
			    'django.contrib.auth.backends.ModelBackend',
			]
			```
		- add search backend to `settings.py`:
			```py
			HAYSTACK_CONNECTIONS = {
			    'default': {
			        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
					},
				}
			```

		- update databases in `settings.py`:

			```py
			DATABASES = {
			    'default': {
			        'ENGINE': 'django.db.backends.sqlite3',
			        'NAME': BASE_DIR / 'db.sqlite3',
			        'USER': '',
			        'PASSWORD': '',
			        'HOST': '',
			        'PORT': '',
			        'ATOMIC_REQUESTS': True,
			    }
			}
			```

		- update `urls.py`:

			```py
			...
			from django.apps import apps
			from django.urls import include
			...

			urlpatterns = [
			    path('i18n/', include('django.conf.urls.i18n')),
			    # The Django admin is not officially supported; expect breakage.
			    # Nonetheless, it's often useful for debugging.
			    path('admin/', admin.site.urls),
			    path('', include(apps.get_app_config('oscar').urls[0])),
			]

			```

		- migrate oscar changes

			```sh
			python manage.py makemigrations
			python manage.py migrate
			```

		- add order pipeline settings to `settings.py`:

			```py
			OSCAR_INITIAL_ORDER_STATUS = 'Pending'
			OSCAR_INITIAL_LINE_STATUS = 'Pending'
			OSCAR_ORDER_STATUS_PIPELINE = {
			    'Pending': ('Being processed', 'Cancelled',),
			    'Being processed': ('Processed', 'Cancelled',),
			    'Cancelled': (),
			}
			```

		- [adding country data](https://django-oscar.readthedocs.io/en/3.1/internals/getting_started.html#initial-data):

			```sh
			$ python manage.py oscar_populate_countries --no-shipping
			```

			- to add countries as shipping options:
				- open the admin page: http://127.0.0.1:8000/admin/address/country/
				- in the search bar, type "united states"
				- click "United States"
				- make sure "Is Shipping Country" is checked
				- set the Display order (optional)
				- click 'save'
				- do the same for any other countries shipping should be available for


	- setting up `oscar-django` payment support:
		- `django-oscar-paypal`:
			```sh
			$ pip install django-oscar-paypal
			$ python manage.py syncdb
			```

		- if `AttributeError: 'SessionStore' object has no attribute '_session_cache'` error is encountered, [try clearing cookies on](https://stackoverflow.com/a/27181817/6158303) `localhost` and `127.0.0.1`


---

<a name="initial_data"></a>
2. ##### providing initial data via data migration

		- dumping:
			```sh
			$ python manage.py dumpdata --exclude=auth --exclude=address --exclude=contenttypes --indent=4 --exclude='admin.logentry' --exclude='sessions.session' --exclude='analytics.userproductview' --output=dehy/fixtures/dumps/jan20.json --exclude=thumbnail --exclude=basket
			```

	work in progress, see here: https://codeinthehole.com/tips/prefer-data-migrations-to-initial-data/

---
<a name="customizing_oscar"></a>
3. ##### customizing oscar

	[**REQUIRED**] [Fork the Oscar app](https://django-oscar.readthedocs.io/en/3.1/topics/customisation.html#fork-the-oscar-app)
	 Before customizing any existing functionality, this step must be done:
	```sh
	$ mkdir $PROJECT_NAME/$APP_FOLDER
	$ touch $PROJECT_NAME/$APP_FOLDER/__init__.py
	```

	<a name="edit_product_model"></a>
	- ###### adding a field to an existing Product model
		1. create/override the 'catalogue' app

			```sh
			./manage.py oscar_fork_app catalogue $PROJECT_NAME/$APP_FOLDER
			```
			in `settings.py`, replace `oscar.apps.catalogue.apps.CatalogueConfig` with `dehy.apps.catalogue.apps.CatalogueConfig`

		2. add desired changes to `dehy/apps/catalogue/models.py`:
			```py
			# dehy/apps/catalogue/models.py

			from django.db import models
			from datetime import datetime
			from oscar.apps.catalogue.abstract_models import AbstractProduct

			class Product(AbstractProduct):
				last_edited = models.DateTimeField(auto_now=True, verbose_name="Last Edited", editable=False)
				created = models.DateTimeField(auto_now_add=True, editable=False)

				def save(self, *args, **kwargs):
					super().save(*args, **kwargs)

			from oscar.apps.catalogue.models import *
			```

		3. apply the changes to the backend

			```
			./manage.py makemigrations catalogue
			./manage.py migrate catalogue
			```

	<a name="edit_product_model"></a>
	- ###### editing product display in dashboard

		1. 'fork' the base 'dashboard' app

			```sh
			$ ./manage.py oscar_fork_app dashboard $PROJECT_NAME/$APP_FOLDER
			```
			Replace the entry `'oscar.apps.dashboard.apps.DashboardConfig'` with `'dehy.apps.dashboard.apps.DashboardConfig'` in INSTALLED_APPS

		2. 'fork' the catalogue dashboard app:

				```sh
				$ ./manage.py oscar_fork_app catalogue_dashboard $PROJECT_NAME/$APP_FOLDER
				```

		3. Replace `'oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig'` with `'dehy.apps.dashboard.catalogue.apps.CatalogueDashboardConfig'` in INSTALLED_APPS

			```py
			INSTALLED_APPS = [
				...
				'dehy.apps.dashboard.apps.DashboardConfig',
				'dehy.apps.dashboard.catalogue.apps.CatalogueDashboardConfig',
				...
			]
			```
		3. create tables file
			```
			$ touch $PROJECT_NAME/$APP_FOLDER/dashboard/catalogue/tables.py
			```

		4. make changes to tables file:
			```py
			from oscar.apps.dashboard.tables import DashboardTable
			from dehy.apps.catalogue.models import Product
			from django_tables2 import A, Column, LinkColumn, TemplateColumn
			from django.utils.translation import gettext_lazy as _

			class ProductTable(DashboardTable):

				...
				stock_records = TemplateColumn(
					verbose_name=_('Stock HELLO'),
					template_name='oscar/dashboard/catalogue/product_row_stockrecords.html',
					orderable=False)

			```

	<a name="edit_staff"></a>
	- ###### modifying staff models/permissions

		```sh
		$ ./manage.py oscar_fork_app partner $PROJECT_NAME/$APP_FOLDER
		```

		Replace the entry `'oscar.apps.partner.apps.PartnerConfig'` with `'dehy.apps.partner.apps.PartnerConfig'` in INSTALLED_APPS

	<a name="edit_views"></a>
	- ###### [modifying an existing view](https://django-oscar.readthedocs.io/en/3.1/howto/how_to_customise_a_view.html), in this example, the `ProductDetailView` within the `catalogue` app

		create the views file

		```sh
		$ touch $PROJECT_NAME/$APP_FOLDER/catalogue/views.py
		```

		```py
		# dehy/apps/catalogue/views.py
		from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView

		class ProductDetailView(CoreProductDetailView):
			template_name = 'catalogue/product.html'
		```
		since we're referencing a custom template file, we'll also need to create it and ensure the templates folder can be found

	<a name="customising_template"></a>
	- ###### customizing an oscar template

		create the folder:

		```sh
		$ mkdir $PROJECT_NAME/$APP_FOLDER/templates
		```

		add folder directory to `settings.py`
		```py
		TEMPLATES = [
			{
				'BACKEND': 'django.template.backends.django.DjangoTemplates',
				'DIRS': [BASE_DIR / 'templates'], ## <<< here
				'APP_DIRS': True,
				...
			},
		]
		```

		```py
		# templates/catalogue/product.html

		{% extends "layout.html" %}
		{% load history_tags %}
		...
		pass
		## <your code edits here>
		...
		```

	<a name="default_currency"></a>
	- ###### changing oscar's default currency
		```py
		OSCAR_DEFAULT_CURRENCY = 'USD'
		```

	<a name="fix_images"></a>
	- ###### making images show
		> NOTE: when uploading images within the dashboard make sure the image location exists
		within the media folder

		- update `urls.py`:
			```py
			# urls.py
			...
			from django.conf import settings
			from django.conf.urls.static import static
			...

			urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

			```

		- update `settings.py`:
			```py
			STATIC_URL = '/static/'
			STATIC_ROOT = BASE_DIR / 'static'

			# URL that handles the media served from MEDIA_ROOT. Make sure to use a
			# trailing slash if there is a path component (optional in other cases).
			# Examples: "http://media.lawrence.com", "http://example.com/media/"
			MEDIA_URL = '/media/'
			MEDIA_ROOT = BASE_DIR / "media"
			```

	<a name="dashboard_form_edit"></a>
	- ###### Editing which fields are displayed for a given Product variant within the [django-oscar dashboard](https://django-oscar.readthedocs.io/en/stable/howto/how_to_customise_models.html#customising-dashboard-forms)

		- create the forms file to override it
			```sh
			$ touch $PROJECT_NAME/$APP_FOLDER/dashboard/catalogue/forms.py
			```

		- required imports:
			```py
			# $PROJECT_NAME/$APP_FOLDER/dashboard/catalogue/forms.py

			from django import forms
			from dehy.apps.catalogue.models import Product
			from oscar.apps.dashboard.catalogue import forms as base_forms
			```

		- finished product (pun):

			```py
			from django import forms
			from dehy.apps.catalogue.models import Product
			from oscar.apps.dashboard.catalogue import forms as base_forms

			class ProductForm(base_forms.ProductForm):

				class Meta(base_forms.ProductForm.Meta):
					model = Product
					fields = [
						'title', 'upc', 'description', 'length', 'width', 'height', 'weight', 'is_public',
						'is_discountable', 'structure', 'slug', 'meta_title',
						'meta_description']
					widgets = {
						'structure': forms.HiddenInput(),
						'meta_description': forms.Textarea(attrs={'class': 'no-widget-init'})
					}

				def __init__(self, *args, **kwargs):
					super().__init__(*args, **kwargs)
					parent = kwargs.get('parent', None)
					if not parent:
						self.delete_variant_shipping_fields()

				def delete_variant_shipping_fields(self):
					"""
					Removes any fields not needed for parent class, e.g variant-specific fields needed
					for shipping, weight/dimensions, etc.
					"""
					for field_name in ['weight', 'length', 'width', 'height']:
						if field_name in self.fields:
							del self.fields[field_name]
			```

		- **IMPORTANT**: Do __NOT__ import the oscar apps at the bottom of the file like one might normally do, ie.
			`from oscar.apps.dashboard.catalogue.forms import * `, else your changes will not be used

	<a name="modify_urls"></a>
	- ###### modifying urls by overriding [the default oscar app](https://django-oscar.readthedocs.io/en/3.1/howto/how_to_change_a_url.html)

		changing the default catalogue url structure from:
			- http://127.0.0.1:8000/catalogue/
			- http://127.0.0.1:8000/catalogue/pear_10/
			- http://127.0.0.1:8000/catalogue/catagory/seasonal/

		to something more sane/elegant:
			- http://127.0.0.1:8000/shop/ - catalogue homepage
			- http://127.0.0.1:8000/shop/p/pear - specific **p**roduct
			- http://127.0.0.1:8000/shop/citrus - category

		http://127.0.0.1:8000/shop/
		in our case, for namespacing reasons, we couldn't simply put the `apps.py` file in our `$PROJECT_NAME` directory because our `$APP_FOLDER` is named 'apps'

		- create `apps.py` and `__init__.py`
			```sh
			$ touch $PROJECT_NAME/$APP_FOLDER/apps.py && touch $PROJECT_NAME/$APP_FOLDER/__init__.py
			```

		- `dehy/apps/apps.py`:

			```py
			# dehy/apps/apps.py
			from oscar import config
			from django.urls import path

			class ShopConfig(config.Shop):
				name = 'dehy'
				namespace = 'dehy'

				# Override get_urls method
				def get_urls(self):
					urlpatterns = super().get_urls()

					catalog_test = lambda x: (hasattr(x, 'namespace') and x.namespace is "catalogue")
					if any((hasattr(x, 'namespace') and x.namespace=="catalogue") for x in urlpatterns):
						ix = list(map(catalog_test, urlpatterns)).index(True)
						if ix:
							urlpatterns.pop(ix)

					urlpatterns += [
						path('shop/', self.catalogue_app.urls, name='shop'),
						# path('shop/', self.extra_view.as_view(), name='extra'),
						# all the remaining URLs, removed for simplicity
						# ...
					]
					print('\nurlpatterns: ', urlpatterns)
					# return self.post_process_urls(urls)
					return urlpatterns
			```

		- note the namespacing in `dehy/__init__.py`:
			```py
			default_app_config = 'dehy.apps.apps.ShopConfig'
			```

		- update `urls.py`: replace `path('', include(apps.get_app_config('oscar').urls[0])),` with `path('', include(apps.get_app_config('dehy').urls[0])),`

		- update catalogue app specific urls in `$PROJECT_NAME/$APP_FOLDER/catalogue/apps.py`, and remove the old, unused urlpatterns:
			```py
			import oscar.apps.catalogue.apps as apps
			from django.urls import include, path

			class CatalogueConfig(apps.CatalogueConfig):
				name = 'dehy.apps.catalogue'

				def get_urls(self):
					urls = super().get_urls()
					disabled_url_names = ['detail', 'category']
					for urlpattern in urls[:]:
						if hasattr(urlpattern, 'name') and (urlpattern.name in disabled_url_names):
							urls.remove(urlpattern)

					urls += [
						path('', self.catalogue_view.as_view(), name='index'),
						path('p/<slug:product_slug>', self.detail_view.as_view(), name='detail'),
						path('<slug:category_slug>', self.category_view.as_view(), name='category'),
					]

					return self.post_process_urls(urls)
			```

		- modify `get_absolute_url()` function within `models.py`:
			```py
			...
			from django.urls import reverse
			from oscar.models.fields.slugfield import SlugField
			from oscar.apps.catalogue.abstract_models import AbstractCategory, AbstractProduct
			from django.utils.translation import gettext_lazy as _

			class Product(AbstractProduct):
				...
				def get_absolute_url(self):
					"""
					Return a product's absolute URL
					"""
					return f"{reverse('catalogue:detail', kwargs={'product_slug': self.slug})}"

			class Category(AbstractCategory):
				slug = SlugField(_('Slug'), max_length=255, db_index=True, unique=True)

				def get_url_cache_key(self):
					current_locale = get_language()
					cache_key = 'CATEGORY_URL_%s_%s' % (current_locale, self.slug)
					return

				def _get_absolute_url(self, parent_slug=None):
					"""
					Our URL scheme means we have to look up the category's ancestors. As
					that is a bit more expensive, we cache the generated URL. That is
					safe even for a stale cache, as the default implementation of
					ProductCategoryView does the lookup via primary key anyway. But if
					you change that logic, you'll have to reconsider the caching
					approach.
					"""

					return reverse('catalogue:category', kwargs={
						'category_slug': self.get_full_slug(parent_slug=parent_slug)
					})
			```

	<a name="disable_feature"></a>
	- ###### [disabling](https://django-oscar.readthedocs.io/en/stable/howto/how_to_disable_an_app_or_feature.html#how-to-disable-oscar-feature) one of oscar's builtin features

		within `settings.py`:
			```py
			...
			OSCAR_HIDDEN_FEATURES = "reviews"
			...
			```

	<a name="edit_homepage"></a>
	- ###### changing the oscar homepage (theorizing)

		- remove `urlpattern` references to 'home' and 'catalogue'  within `apps/apps.py`
			```py
			class ShopConfig(config.Shop):
				name = 'dehy'
				namespace = 'shop'

				def get_urls(self):
					urls_to_remove = []
					urlpatterns = super().get_urls()
					for pattern in urlpatterns:
						if hasattr(pattern, 'name'):
							name = getattr(pattern, 'name', None)
							if name == 'home':
								urls_to_remove.append(pattern)

						if hasattr(pattern, 'namespace'):
							namespace = getattr(pattern, 'namespace', None)
							if namespace == 'catalogue':
								urls_to_remove.append(pattern)

					for pattern in urls_to_remove:
						urlpatterns.remove(pattern)

			```

		- create the custom file under `$PROJECT_NAME/views.py` and add the following:
			```py
			# dehy/views.py

			from django.views.generic import TemplateView

			class HomeView(TemplateView):
			    template_name = "home.html"
			```

		- create the custom template file under `$PROJECT_NAME/templates` and add the following:
			```html
			<!-- dehy/templates/home.html -->

			{% extends "oscar/layout.html" %}

			{% load i18n %}
			{% load product_tags %}

			{% block title %}
			{% trans "Home" %} | {{ block.super }}
			{% endblock %}

			<h1>test 123</h1>
			```

		- make sure its hooked up in `urls.py`:
			```py
			...
			from . import views

			urlpatterns = [
				...
				path('', views.HomeView.as_view(), name='home'),
				path('', include(apps.get_app_config('dehy').urls[0])),
				...
			]
			```
		- optionally, change [`OSCAR_HOMEPAGE`](https://django-oscar.readthedocs.io/en/3.1/ref/settings.html?highlight=THUMBNAIL#oscar-homepage) to point to the newly created url:
			```py
			# settings.py
			...
			OSCAR_HOMEPAGE = reverse_lazy('home')
			...
			```

---
<a name="django_oscar_paypal"></a>
1. ##### implementing paypal payments with [django-oscar-paypal](https://django-oscar-paypal.readthedocs.io/en/latest/express.html)

	-

---

<a name="git_commands"></a>
4. ###### various git commands

	1. authenticating (Sometimes required prior to pushing)

		```sh
		$ ssh -vT git@github.com
		```

---

<a name="server_cli"></a>
5. ###### various CLI commands

	1. connecting to AWS instance via [ssh](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html):

		```sh
		$ ssh -i /path/my-key-pair.pem my-instance-user-name@my-instance-public-dns-name
		```
