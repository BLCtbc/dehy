# Provisioning notes, how-to's, etc. for a custom django-oscar deployment

1. [installation and setup](#installation)
	- [server side config files](#server_config)
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
	- [overriding base templates](#base_layouts_override)
4. [overriding oscar dashboard and adding custom menu item](#oscar_nav_override)
4. [implementing paypal payment support with django-oscar-payapl](#django_oscar_paypal)
5. [linux cli commands](#server_cli)
	- [connecting to AWS](#connecting_to_AWS)
6. [git commands](#git_commands)
	- [authenticating github][#git_authentication]
7. [troubleshooting](#troubleshooting)
	- [postgres issues](#postgresql)
	- [issues with using custom User model](#custom_user_model)
8. [clearing sorl thumbnail media cache](#clear_sorl_image_cache)
9. [running local django server over https](#local_django_https)
10. [integrating stripe with django-oscar](#stripe_integration)
11. [downloading and installing a package on debian](#debian_package_install)
12. [setting up email sending and receiving on AWS SES](#aws_ses_integration)
13. [enabling ftp access](#enable_ftp)
14. [adding the ability to create shipping events](#create_shipping_event_type)
15. [creating oscar email template via backend](#create_oscar_email_template)
16. [adding new/custom communication event type](#adding_new_communication_event_type)
17. [creating a custom conditional for specific shipping code and value requirement](#custom_shipping_condition)
18. [quickbooks API setup](#quickbooks_api_setup)
19. [installing and setting up celery+rabbitmq](#celery_rabbitmq)
---

Note, any changes made to `settings.py` might require restarting the server in order to take affect

1. ##### <a name="installation"></a> Creating new django project with [oscar-django](https://django-oscar.readthedocs.io/en/3.1/internals/getting_started.html#install-oscar-and-its-dependencies)
	- aws setup
		- updating packages:
			```sh
			% sudo apt update
			% sudo apt upgrade
			```

		- setting key permissions and connecting to your AWS instance (most instructions from [here](https://dev.to/rmiyazaki6499/deploying-a-production-ready-django-app-on-aws-1pk3))
			```sh
			$ cd Documents/$REPO_FOLDER
			$ chmod 400 DEHY.cer # changes permissions on cert file (required)
			$ ssh -i "DEHY.cer" admin@ec2-3-135-111-34.us-east-2.compute.amazonaws.com
			```

		- setting up firewall and installing dependencies
			```sh
			% sudo apt-get install ufw
			% sudo ufw enable
			% sudo apt install git python3-venv python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx gunicorn curl
			% sudo ufw allow OpenSSH && sudo ufw allow 'Nginx Full'
			```

	- install dependencies + virtual env setup
		cloning the repo (might have to [authenticate github first](#connecting_to_AWS))
			```sh
			$ git clone git@github.com:BLCtbc/dehy.git
			```

			```sh
			$ python3.7 -m venv venv # create the virtual environment
			$ source venv/bin/activate # activate the virtual environment
			$ (venv) pip install --upgrade pip
			$ (venv) pip install -r requirements.txt
			$ (venv) export PROJECT_NAME=dehy && export APP_FOLDER=apps
			```

		required extra dependencies (skip if you installed via `requirements.txt`)
			```sh
			$ (venv) pip install 'django-oscar[sorl-thumbnail]' # should also install django and various other requirements
			$ (venv) pip install pycountry # additional dependency
			$ (venv) pip install psycopg2-binary # PostgreSQL requirement
			```
			```sh
			$ (venv) django-admin startproject $PROJECT_NAME # rename to w/e your project name is
			$ (venv) mv $PROJECT_NAME temp && mv temp/manage.py manage.py && mv temp/$PROJECT_NAME $PROJECT_NAME && rm -r temp #changes filestructure
			```

	- database setup:
		#### setup database
		* start the server and login
		    * linux
			    ```
			    $ sudo -u postgres psql
			    ```
		    * mac (assuming installation was via [homebrew](https://wiki.postgresql.org/wiki/Homebrew))
			    ```
				$ brew install postgresql
			    $ brew services start postgresql
			    $ psql postgres
			    ```
				> see [here](https://stackoverflow.com/questions/13410686/postgres-could-not-connect-to-server) for troubleshooting methods

		* create database/user with [optimal](https://docs.djangoproject.com/en/3.0/ref/databases/#optimizing-postgresql-s-configuration) settings

			```sql
			postgres=# CREATE DATABASE dehy;
			postgres=# CREATE USER dehydevuser WITH PASSWORD 'penileZZ44yN0tT420';
			postgres=# ALTER ROLE dehydevuser SET client_encoding TO 'utf8';
			postgres=# ALTER ROLE dehydevuser SET default_transaction_isolation TO 'read committed';
			postgres=# ALTER ROLE dehydevuser SET timezone TO 'America/Chicago';
			```

		* grant permissions, then quit
			```sql
			postgres=# GRANT ALL PRIVILEGES ON DATABASE dehy TO dehydevuser;
			-- grant permissions on the default database also, for testing
			postgres=# GRANT ALL PRIVILEGES ON DATABASE postgres TO dehydevuser;
			postgres=# \q
			```

		* or if you have an existing database and want to make a copy:
			```sql
			postgres=# CREATE DATABASE dehy_staging WITH TEMPLATE dehy OWNER dehydevuser;
			postgres=# GRANT ALL PRIVILEGES ON DATABASE dehy_staging TO dehydevuser;
			```

		<a name="re_instantiate_database"></a>
		* If you need to first delete an existing database... re-instantiating postgresql database
			steps 1 and 2 from [here](https://www.postgresqltutorial.com/postgresql-administration/postgresql-drop-database/)
			1. dropping database with no connections

				```sql
				postgres=# DROP DATABASE dehy;
				```

			2. dropping database WITH active connections

				```sql
				-- the output from this command is much easier to read within pgadmin, although not relaly necessary
				postgres=# SELECT * FROM pg_stat_activity WHERE datname = 'dehy_staging';

				-- if you run this command within pgadmin you will lose connection
				SELECT pg_terminate_backend (pg_stat_activity.pid)
				FROM pg_stat_activity
				WHERE pg_stat_activity.datname = 'dehy_staging';

				--
				DROP DATABASE dehy_staging;
				```

			3. delete all migration files:
				test the pattern:
					`ls -la ./dehy/appz/*/migrations/*.py`

				remove migration files:
					`rm -r ./dehy/appz/*/migrations/*.py`
					<!-- `rm -rf ./dehy*/__pycache__` -->

			4. remove references to models within files (since the model instances no longer exist, and will cause errors)

				i commented this whole file out:
				```py
				# appz/shipping/repository.py
				...
				# from dehy.appz.generic.models import FedexAuthToken as FedexAuthTokenModel
				...
				```

			5. replace the oscar migration files

				```sh
				# repeat this for all forked oscar apps...
				# current list: address, basket, catalogue, customer, order, partner, payment, shipping
				export APP_NAME=basket
				cp -R venv/lib/python3.7/site-packages/oscar/apps/$APP_NAME/migrations dehy/appz/$APP_NAME
				```

			6. makemigrations:
				```sh
				python manage.py makemigrations

				# need to specify the app name for any custom (non-oscar) apps
				python manage.py makemigrations generic
				python manage.py makemigrations recipes
				```

			7. migrate:
				`python manage.py migrate`


			8. load the fixtures (see below)

			9. populate the country objects `python manage.py oscar_populate_countries`


		- loading fixtures:
			```sh
			python fixture_creator.py # file must be placed+called in same directory as manage.py
			```

		- loading images into database:
			```sh
			python get_product_images.py # file must be placed+called in same directory as manage.py
			```

	- create and setup the `.env` file:

		```sh
		$ touch $PROJECT_NAME/.env
		```

		contents of `$PROJECT_NAME/.env`:
		```sh
		# Development Environment settings
		DEBUG=on
		SECRET_KEY='secret-key'
		ALLOWED_HOSTS=['*']
		DATABASE_URL=sqlite:///db.sqlite3
		REDIS_CACHE_URL=redis://use
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
			TIME_ZONE = 'America/Chicago'
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

			- use the 'no-shipping' option so that all countries aren't available to be shipped to. Then, to add countries as shipping options:
				- open the admin page: http://127.0.0.1:8000/admin/address/country/
				- in the search bar, type "united states"
				- click "United States"
				- make sure "Is Shipping Country" is checked
				- set the Display order (optional)
				- click 'save'
				- do the same for any other countries shipping should be available for (Canada for example)

	<a name="server_config"></a>
	- server config files

		- gunicorn
			- socket file:

				```
				[Unit]
				Description=gunicorn socket for dehy

				[Socket]
				ListenStream=/run/gunicorn.sock

				[Install]
				WantedBy=sockets.target
				```

			- service file (log file locations might need correcting)

				```
				[Unit]
				Description=gunicorn daemon for dehy
				Requires=gunicorn.socket
				After=network.target

				[Service]
				User=admin
				Group=www-data
				WorkingDirectory=/home/admin/dehy
				ExecStart=/home/admin/dehy/venv/bin/gunicorn \
				--access-logfile access.log \
        		--error-logfile error.log \
				--workers 3 \
				--bind unix:/run/gunicorn.sock \
				dehy.wsgi:application

				[Install]
				WantedBy=multi-user.target
				```

		- nginx

			```
			server {
			        listen 80;
			        server_name dehygarnish.com 3.135.111.34;

			        location = /favicon.ico { access_log off; log_not_found off; }
			        location /static {
			                alias /home/admin/dehy/static;
			        }

			        location / {
			                include proxy_params;
			                proxy_pass http://unix:/run/gunicorn.sock;
			        }
			}
			```




---

<a name="initial_data"></a>
2. ##### providing initial data via data migration
	*NOTE*: when uploading fixtures via `fixture_creator.py` be sure to implement the neccessary changes to `catalogues/models.py`, ie. you must fork the app oscar_fork_app catalogue`

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


		- create `apps.py` and `__init__.py`
			```sh
			$ touch $PROJECT_NAME/__init__.py
			```

		- `dehy/__init__.py`:
			```py
			default_app_config = 'dehy.apps.ShopConfig'
			```

		- `dehy/apps.py`:

			```py
			from oscar import config
			from django.urls import path

			class ShopConfig(config.Shop):
				name = 'dehy'
				namespace = 'shop'

				# Override get_urls method
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


					urlpatterns += [
						path('shop/', self.catalogue_app.urls, name='shop'),
						# path('shop/', self.extra_view.as_view(), name='extra'),
						# all the remaining URLs, removed for simplicity
						# ...
					]

					return urlpatterns
			```

		if `$APP_FOLDER` is named 'apps', simply put the `apps.py` file under `$PROJECT_NAME/apps`
		and change the namespacing in `$PROJECT_NAME/__init__.py` to `'dehy.apps.apps.ShopConfig'`

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

			{% extends "layout.html" %}

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

		- troubleshooting
			- if `AttributeError: 'SessionStore' object has no attribute '_session_cache'` error is encountered, [try clearing cookies on](https://stackoverflow.com/a/27181817/6158303) `localhost` and `127.0.0.1`


	<a name="base_layouts_override"></a>
	- ###### overriding base templates (theorizing)
		- follow the directions [here](https://django-oscar.readthedocs.io/en/3.1/howto/how_to_customise_templates.html#method-1-forking)

		- list of apps to fork to override `layout.html`:
			- checkout: `./manage.py oscar_fork_app checkout dehy/appz`
			- dashboard (optional): `./manage.py oscar_fork_app dashboard dehy/appz`

		- list of apps to fork to override `layout_2_col.html`:
			- catalogue: `./manage.py oscar_fork_app catalogue dehy/appz`
			- search: `./manage.py oscar_fork_app search dehy/appz`
			- basket: `./manage.py oscar_fork_app basket dehy/appz`
			- customer: `./manage.py oscar_fork_app customer dehy/appz`

		- after forking all of the above ups, create copies of the aforementioned oscar template directories:
			- `venv/lib/python3.7/site-packages/oscar/templates/basket` -> `templates/basket` -- repeat for all required apps

		- list of files where an override is needed:
			- `layout_2_col.html`
			- `layout_3_col.html`
			- `basket/basket.html`
			- `checkout/checkout.html`
			- `checkout/layout.html`
			...
			..way too many to list..
			suggestion: use a regex pattern something like this: `oscar\/([\w]+\.html)` and just replace all
			regex for nested: `oscar\/([\w]+\/[\w]+\.html)`

---
<a name="oscar_nav_override"></a>
1. ##### adding a custom model item to oscar's builtin dashboard
	initially started attempting to implement this from the [official documentation](https://django-oscar.readthedocs.io/en/3.1/howto/how_to_configure_the_dashboard_navigation.html), wound up using [this how-to article](https://levelup.gitconnected.com/creating-an-oscar-app-with-dashboard-part-2-6283dd24304) as a guide

	- create the custom apps:
		```sh
		$ mkdir dehy/appz/recipes
		$ mkdir dehy/appz/dashboard/recipes
		$ ./manage.py startapp recipes dehy/appz/recipes
		$ ./manage.py startapp recipes dehy/appz/dashboard/recipes
		```

	- create model and views, hookup the apps and the urls

		```py
		##############################
		# dehy/appz/recipes/apps.py

		from django.apps import AppConfig

		class RecipesConfig(AppConfig):
			default_auto_field = 'django.db.models.BigAutoField'
			name = 'dehy.appz.recipes'
			namespace = 'recipes'
			label = 'recipes'

		##############################
		# dehy/appz/recipes/models.py
		from django.db import models
		from django.contrib.postgres.fields import ArrayField
		from oscar.models.fields import AutoSlugField

		class Recipe(models.Model):
			name = models.CharField(max_length=100, default="", help_text='Name of the recipe')
			description = models.TextField(help_text='A short introduction about the recipe, origin, summary, etc.')
			ingredients = ArrayField(models.CharField(max_length=50))
			slug = AutoSlugField(max_length=50, unique=True, populate_from=name, editable=True)
			date_created = models.DateField(auto_now_add=True, editable=False)
			last_modified = models.DateField(auto_now=True, editable=False)

		##############################
		# dehy/settings.py
		INSTALLED_APPS = [
			...
			'dehy.appz.recipes.apps.RecipesConfig',
			'dehy.appz.dashboard.recipes.apps.RecipesDashboardConfig',
			...
		]

		##############################
		# dehy/appz/recipes/views.py
		from django.shortcuts import render
		from django.views.generic import ListView, DetailView, TemplateView
		from .models import Recipe

		class RecipesView(TemplateView):
			template_name = "dehy/recipes.html"

		class RecipeListView(ListView):
			model = Recipe
			context_object_name = "recipes"
			# template_name = "dehy/recipes.html"

		class RecipeDetailView(DetailView):
		    model = Recipe
		    template_name = "dehy/recipes.html"
		    context_object_name = "recipe"
		    slug_field = 'slug'
		    slug_url_kwarg = 'slug'

		##############################
		# dehy/appz/recipes/urls.py
		from django.urls import path
		from . import views

		urlpatterns = [
			path('recipes/', views.RecipesView.as_view(), name='recipes'),
			path('recipes/<slug:recipe_slug>', views.RecipeDetailView.as_view(), name='recipe_details'),
		]

		##############################
		# dehy/urls.py
		from django.apps import apps
		from django.urls import include, path
		from django.contrib import admin

		urlpatterns = [
			path('admin/', admin.site.urls),
			path('', include('dehy.appz.recipes.urls'), name='recipes'),
			path('', include(apps.get_app_config('dehy').urls[0])),
		]
		```

	- dashboard specific changes:
		```py
		# dehy/appz/dashboard/apps.py

		from django.apps import apps
		from django.urls import include, path
		from django.utils.translation import gettext_lazy as _
		from oscar.core.loading import get_class
		import oscar.apps.dashboard.apps as oscar_apps

		class DashboardConfig(oscar_apps.DashboardConfig):
			name = 'dehy.appz.dashboard'
			label = 'dashboard'
			verbose_name = _('Dashboard')
			namespace = 'dashboard'
			permissions_map = {
				'index': (['is_staff'], ['partner.dashboard_access']),
			}

			def ready(self):
				super().ready()
				self.recipes_app = apps.get_app_config('recipes_dashboard')

			def get_urls(self):
				urls = super().get_urls()
				urls += [
					path('recipes/', include(self.recipes_app.urls[0]))
				]
				return self.post_process_urls(urls)

		# dehy/appz/dashboard/recipes/apps.py
		from oscar.core.application import OscarDashboardConfig
		from django.urls import path
		from oscar.core.loading import get_class
		import oscar.apps.catalogue.apps as apps
		from django.utils.translation import gettext_lazy as _

		class RecipesDashboardConfig(OscarDashboardConfig):
			default_auto_field = 'django.db.models.BigAutoField'
			name = 'dehy.appz.dashboard.recipes'
			label = 'recipes_dashboard'
			verbose_name = _('Recipes')
			namespace = 'recipes'
			default_permissions = ['is_staff']
			permissions_map = _map = {
		        'recipe-create': (['is_staff'],
		                                     ['partner.dashboard_access']),
		        'recipe-list': (['is_staff'], ['partner.dashboard_access']),
		        'recipe-delete': (['is_staff'],
		                                     ['partner.dashboard_access']),
		        'recipe-update': (['is_staff'],
		                                     ['partner.dashboard_access']),
		    }


			def ready(self):
				super().ready()
				self.recipes_list_view = get_class('dashboard.recipes.views', 'RecipeListView')
				self.recipes_create_view = get_class('dashboard.recipes.views', 'RecipeCreateView')
				self.recipes_update_view = get_class('dashboard.recipes.views', 'RecipeUpdateView')
				self.recipes_delete_view = get_class('dashboard.recipes.views', 'RecipeDeleteView')

			def get_urls(self):
				urls = super().get_urls()
				urls += [
					path('', self.recipes_list_view.as_view(), name='recipe-list'),
					path('create/', self.recipes_create_view.as_view(), name='recipe-create'),
					path('update/<int:pk>/', self.recipes_update_view.as_view(), name='recipe-update'),
					path('delete/<int:pk>/', self.recipes_delete_view.as_view(), name='recipe-delete'),
				]
				return self.post_process_urls(urls)

		# dehy/appz/dashboard/recipes/views.py
		from django.apps import apps
		from django.urls import include, path
		from django.utils.translation import gettext_lazy as _
		from oscar.core.loading import get_class
		import oscar.apps.dashboard.apps as oscar_apps

		class DashboardConfig(oscar_apps.DashboardConfig):
			name = 'dehy.appz.dashboard'
			label = 'dashboard'
			verbose_name = _('Dashboard')
			namespace = 'dashboard'
			permissions_map = {
				'index': (['is_staff'], ['partner.dashboard_access']),
			}

			def ready(self):
				super().ready()
				self.recipes_app = apps.get_app_config('recipes_dashboard')

			def get_urls(self):
				urls = super().get_urls()
				urls += [
					path('recipes/', include(self.recipes_app.urls[0]))
				]
				return self.post_process_urls(urls)

		# dehy/appz/dashboard/recipes/forms.py
		from django import forms
		from django.db.models import Q
		from django.utils.translation import gettext_lazy as _
		from oscar.core.loading import get_model

		Recipe = get_model('recipes', 'Recipe')

		class RecipeSearchForm(forms.Form):

			name = forms.CharField(label=_('Recipe name'), required=False)
			ingredients = forms.CharField(label=_('Ingredients list'), required=False)
			slug = forms.SlugField(label=('Slug'), required=False)

			def is_empty(self):
				d = getattr(self, 'cleaned_data', {})
				def empty(key): return not d.get(key, None)
				return empty('name') and empty('ingredients')

			def apply_ingredient_filter(self, qs, value):
				words = value.replace(',', ' ').split()
				q = [Q(city__icontains=word) for word in words]
				return qs.filter(*q)

			def apply_name_filter(self, qs, value):
				return qs.filter(name__icontains=value)

			def apply_filters(self, qs):
				for key, value in self.cleaned_data.items():
					if value:
						qs = getattr(self, 'apply_%s_filter' % key)(qs, value)
				return qs

		class RecipeCreateUpdateForm(forms.ModelForm):
			class Meta:
				model = Recipe
				fields = ('name', 'slug', 'ingredients')
		```

	- copy the oscar template files:
		```
		$ mkdir dehy/templates/oscar/dashboard && cp venv/lib/python3.7/oscar/templates/dashboard dehy/templates/oscar/dashboard
		```

---

---
<a name="django_oscar_paypal"></a>
1. ##### implementing paypal payments with [django-oscar-paypal](https://django-oscar-paypal.readthedocs.io/en/latest/express.html)

	-

---

<a name="git_commands"></a>
4. ###### various git commands

	<a name="ssh_key_creation"></a>
	1. [creating an SSH key for github and adding it to your account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)

		```sh
		$ ssh-keygen -t ed25519 -C "bigleagchew@gmail.com" # creating it
		```

		open the file:
		```sh
		$ cat ~/.ssh/id_ed25519.pub #
		```
		copy/paste the output

	<a name="git_authentication"></a>
	2. authenticating

			```sh
			$ ssh -vT git@github.com
			```

		often required if you see this message after trying to `git push` or `git clone` a private repo:
			```
			git@github.com: Permission denied (publickey).
			fatal: Could not read from remote repository.

			Please make sure you have the correct access rights
			and the repository exists.
			```
	<a name="restore_deleted_files_after_commit"></a>
	3. restoring files after committing to git

		First find the commit id of the commit that deleted your file(s)

			```sh
			git log --diff-filter=D --summary
			```

		Then proceed to restore the file(s) by running the following command (note: also works on folders if multiple files need restoring)

			```sh
			git checkout 81eeccf~1 <your-lost-file-name>
			```

	4. (re)adding ssh version of remote url
		[check the ssh keys exist](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/checking-for-existing-ssh-keys):
			```sh
			ls -al ~/.ssh
			```

			```sh
			git remote set-url origin git@github.com:blctbc/dehy.git
			```
---

<a name="server_cli"></a>
5. ###### various CLI commands
	<a name="connecting_to_AWS"></a>
	1. connecting to AWS instance via [ssh](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html):

		```sh
		$ ssh -i /path/my-key-pair.pem my-instance-user-name@my-instance-public-dns-name
		```

		for this project:
		`$ ssh -i DEHY.cer admin@3.135.111.34`

	2. downloading a package
		```sh
		wget
		```

<a name="troubleshooting"></a>
6. ###### troubleshooting

	<a name="postgresql"></a>
		- troubleshooting fresh install:

			```sh
			brew services stop postgresql
			rm -rf "$(brew --prefix)/var/postgres"
			initdb --locale=C -E UTF-8 "$(brew --prefix)/var/postgres"
			brew services start postgresql
			```

		- To check what is running on port 5432, issue the following command on your terminal.
			`$ sudo lsof -i :5432`

		- finding all postgres processes
			`$ ps -ef | grep postgresp`

			output might look something like:

			uid   pid  ppid   C  STIME TTY         TIME    CMD
			```
			504   511   147   0  1:23PM ??         0:00.00 postgres: logger
			504   535   147   0  1:23PM ??         0:00.01 postgres: checkpointer
			504   539   147   0  1:23PM ??         0:00.01 postgres: stats collector
			504  2796   147   0  1:29PM ??         0:00.03 postgres: background writer
			504  3032   147   0  1:30PM ??         0:00.01 postgres: walwriter
			504  3033   147   0  1:30PM ??         0:00.01 postgres: autovacuum launcher
			504  3034   147   0  1:30PM ??         0:00.00 postgres: logical replication launcher
			501  3971   853   0  1:36PM ttys001    0:00.00 grep postgres
			```

			NOTE: the postmaster PID in this case 147, which is the parent pid of most the processes listed

		- stop all postgres processes (requires having postgres installed)
			`$ pg_ctl -D $(psql -Xtc 'show data_directory') stop`

		- kill all postgres processes
			`$ sudo pkill -u postgres` That kills all processes running as user `postgres`
				or
			`$ pkill postgres` That kills all processes named 'postgres'

	<a name="custom_user_model"></a>
	- using a custom user model with django oscar

		follow the steps listed here:
		https://stackoverflow.com/a/53936097/6158303

		- step 1:

			```py
			# settings.py
			...
			AUTH_USER_MODEL = "generic.User"
			...

			# dehy/appz/generic.models

			...
			from oscar.apps.customer.abstract_models import AbstractUser
			...
			class User(AbstractUser):
				stripe_customer_id = models.CharField(_('Stripe Customer ID'), max_length=255, blank=True)

			```

		- step 2:`python manage.py makemigrations`

		- step 3: undo step 1
			```py
			# settings.py
			...
			# AUTH_USER_MODEL = "generic.User"
			...

			# dehy/appz/generic.models

			...
			from oscar.apps.customer.abstract_models import AbstractUser
			...
			#class User(AbstractUser):
			#	stripe_customer_id = models.CharField(_('Stripe Customer ID'), max_length=255, blank=True)

			```

		- step 4: `python manage.py migrate`

		- step 5: redo step 1


	<a name="collecstatic_permissions_errors">
	- permission denied error when running `python manage.py collectstatic --noinput --clear`

		go to the directory `cd /path/to/static/folder/`
		change the owner:group -> if you aren't sure, check the media file owner first and just use those settings:
			`sudo chown -R admin:www-data static/`

		also need to change this, else venv will be deleted after each pull:
			`sudo chown -R admin:www-data venv/`




implementing a continuous deployment workflow on Debian 10+
[adding a self-hosted runner](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners)
[configuring the self-hosted runner as a service](https://docs.github.com/en/actions/hosting-your-own-runners/configuring-the-self-hosted-runner-application-as-a-service)
	```sh
	$ sudo ./svc.sh install
	$ sudo ./svc.sh start
	```
[installing ssm agent on debian running](https://docs.aws.amazon.com/systems-manager/latest/userguide/agent-install-deb.html)

<a name="runner_config_reset"></a>
6. ###### resetting the self-hosted runner config

	1. follow the steps given here
	2. removing existing config (required)
			```sh
			$ cd ~/actions-runner && sudo ./svc.sh stop && sudo ./svc.sh uninstall && ./config.sh remove --token AIZIT75KYJN7TO6JXMXJCRLCA24FI
			```


	3. follow the steps listed in this [github help center](https://docs.github.com/en/actions/hosting-your-own-runners/removing-self-hosted-runners) article to get the token. Should look something like this `./config.sh remove --token AIZIT75KYJN7TO6JXMXJCRLCA24FI`


	4. running the config
			```sh
			$ ./config.sh --url https://github.com/BLCtbc/dehy --token AIZIT75KYJN7TO6JXMXJCRLCA24FI
			$ sudo ./svc.sh install && sudo ./svc.sh start
			```

	5. removing extra shit left behind:
		`rm -rf _temp _tool _actions _PipelineMapping`

	- a note about $GITHUB_WORKSPACE, from https://docs.github.com/en/actions/learn-github-actions/environment-variables:

		> The default working directory on the runner for steps, and the default location of your repository when using the checkout action. For example, /home/runner/work/my-repo-name/my-repo-name.

<a name="clear_sorl_image_cache"></a>
6. ###### clearing out django oscar's thumbnail/sorl's media cache of thumbnails

		```sh
		$ python manage.py thumbnail cleanup && python manage.py thumbnail clear

		```
	after that, restart everything:

		`sudo systemctl daemon-reload && sudo systemctl restart nginx && sudo systemctl restart gunicorn`


<a name="local_django_https"></a>
6. ###### running local django server over https

	```sh
	$ brew install mkcert
	$ mkcert -install
	$ mkcert -cert-file cert.pem -key-file key.pem localhost 127.0.0.1
	$ pip install django-sslserver
	```

	```
	python manage.py runsslserver --certificate cert.pem --key key.pem
	```

8. ###### testing

		if you continuously get `ModuleNotFoundError: No module named 'dehy.functional_tests'`
		even though the modules are clearly visible and discoverable, the issue could be resolved
		by renaming the project folder, as suggested [here](https://stackoverflow.com/a/28476388/6158303)

		the actual command:
		`./manage.py test functional_tests --keepdb -v 3`

		additionally, you should make sure you have
		```sql
		postgres=# GRANT ALL PRIVILEGES ON DATABASE postgres TO dehydevuser;
		postgres=# \q
		```

	fixture used:

		`python manage.py dumpdata --exclude=auth --exclude=address --exclude=contenttypes --indent=4 --exclude='admin.logentry' --exclude='sessions.session' --exclude=analytics --exclude=thumbnail --exclude=basket --exclude=order --exclude=payment --output='fixtures.json'`

		fixing shipping countries:
			```py
			from oscar.core.loading import get_model
			Country = get_model('address', 'Country')
			country_objects = Country.objects.all()
			shippable_countries = ['US', 'CA']
			for country in country_objects:
				if country.iso_3166_1_a2 not in shippable_countries:
					country.is_shipping_country = False
					country.save()
			```

		dumping all:
		`python manage.py dumpdata --all --indent=4 --output='fixtures_all.json'`




<a name='django_view_inserted_into_another_view'></a>
9. ###### insert a django view (child) into another view (parent)

	add the following lines within the parent view's `get()` function:

		```py
		# dehy/appz/checkout/views.py
		...
		response = super().get(request, *args, **kwargs)
		basket_view = BasketView.as_view()(request)
		response.context_data.update({'form': self.form_class(), 'basket_summary_context_data': basket_view.context_data})
		```



<a name='stripe_integration'></a>
10. ###### working with stripe

   ###### integrating sripe with django oscar (some useful info for starting out

	see: https://stackoverflow.com/questions/51243465/how-to-integrate-stripe-payments-gateway-with-django-oscar
	and: https://groups.google.com/g/django-oscar/c/Cr8sBI0GBu0/m/PHRdXX2uFQAJ


	###### some stripe examples:

	<a name='stripe_order_creation'></a>
	1. stripe order creation (from django shell)
		NOTE: the only the country and postal_code are required when supplying an address field

		```py
		from django.conf import settings
		import stripe

		stripe.api_key = settings.STRIPE_SECRET_KEY
		stripe.pkey = settings.STRIPE_PUBLISHABLE_KEY
		stripe.api_version = '2020-08-27; orders_beta=v2'

		####################
		## order with tax ##
		####################

		order = stripe.Order.create(
		  currency="usd",
		  line_items=line_items,
		  payment={
		    "settings": {
		      "payment_method_types": ["card"],
		    },
		  },
		  expand=["line_items"],
		  automatic_tax={
		    "enabled": True,
		  },
		  shipping_details={
		    "address": {
			 "city": "Austin", "country":"US", "postal_code":"78759", "state": "TX"
			},
			"name":"anon"
		  }
		)

		############
		## no tax ##
		############
		order = stripe.Order.create(
		  currency="usd",
		  line_items=line_items,
		  payment={
		    "settings": {
		      "payment_method_types": ["card"],
		    },
		  },
		  expand=["line_items"],
		  automatic_tax={
		    "enabled": True,
		  },
		  shipping_details={
		    "address": {
			  "city": "Gainesville", "country":"US", "postal_code":"32605", "state": "FL"
			},
			"name":"anon"
		  }
		)
		```

	<a name='stripe_order_update'></a>
	2. updating a stripe order (from django shell)

		```py

		shipping_addr = {'first_name': 'kenneth', 'city': 'Austin', 'postcode': '78759', 'country': 'US', 'state': 'TX'}

		## when creating dictionaries that will supply information to stripe, ensure all required info is supplied.
		## For required items that are not necessarily needed to retrieve order info, such as a 'name'
		## use a ternary operator to supply a value, example:

		name = shipping_addr['first_name'] if shipping_addr.get('first_name', None) else 'anon'
		name = f"name {shipping_addr['last_name']}" if shipping_addr.get('last_name', None) else name

		shipping_details = {
			'address': {
				'postal_code': '78759',
				'country': 'US',
				'state': 'TX',
				'city': 'Austin'
			},
			'name': name,
		}

		## when supplying optional information, only add it to the dict if a value is supplied
		## as supplying blank info causes stripe to error, example:
		if shipping_addr.get('line1', None):
			shipping_details['address']['line1'] = shipping_addr['line1']


		## should also ensure currency values are given in cents
		shipping_cost = {
			'shipping_rate_data': {
				'display_name': 'FEDEX_GROUND',
				'type':'fixed_amount',
				'fixed_amount': {
					'amount': str((D('24.49')*100).to_integral()),
					'currency': 'usd'
				},
				'tax_behavior': 'exclusive'
			}
		}

		#######################
		## updating an order ##
		#######################

		order = stripe.Order.modify(
			basket.stripe_order_id,
			line_items=line_items,
			shipping_cost=shipping_cost,
			shipping_details=shipping_details,
			discounts=discounts
		)

		```


1. follow steps 1 - 4 here: https://www.cyberciti.biz/tips/postgres-allow-remote-access-tcp-connection.html
2. find your ip address
3. add firewall rule: `sudo ufw allow from 104.14.25.32 to any port 5432`

sudo ufw allow from 104.14.25.32

<a name="debian_package_install"></a>
10. ###### downloading and installing a package on debian 10 (example)

	```sh
	wget https://github.com/stripe/stripe-cli/releases/download/v1.8.6/stripe_1.8.6_linux_amd64.deb
	head stripe_1.8.6_linux_x86_64.tar.gz # test contents of file
	sudo dpkg -i stripe_1.8.6_linux_amd64.deb
	```


<a name="aws_ses_integration"></a>
11. ###### setting up email sending and receiving on AWS SES (simple email service)

	1. install via pip:
	```sh
	pip install 'django-ses[events]' # the quotes were needed on mac, unsure for linux
	```
	this guide: https://medium.com/hackernoon/the-easiest-way-to-send-emails-with-django-using-ses-from-aws-62f3d3d33efd
	this library: https://github.com/django-ses/django-ses

	2. after configuring a domain identity [here](https://us-east-2.console.aws.amazon.com/ses/home?region=us-east-2#/verified-identities), you will be sent to edit your DNS records [here](https://domains.google.com/registrar/dehygarnish.net/dns)

	the instructions given by amazon say to add 3 CNAME DNS records in the following format:
	type  name													         value
	```
	CNAME 76you5sp74ywmnfhmt5qenbei6xykhrl._domainkey.dehygarnish.net     76you5sp74ywmnfhmt5qenbei6xykhrl.dkim.amazonses.com
	```

	in all 3 of the `name` fields, chop of everything after `._domainkey`, as this is already added automatically by google domains...
	so your DNS record should look like this:
	type  name										   value
	```
	CNAME 76you5sp74ywmnfhmt5qenbei6xykhrl._domainkey  76you5sp74ywmnfhmt5qenbei6xykhrl.dkim.amazonses.com
	```


< name="certbot_integration"></a>
12. ###### installing and setting up certbot (SSL cert)

	follow the instructions here: https://certbot.eff.org/instructions?ws=nginx&os=debianbuster

< name="enable_ftp"></a>
12. ###### enabling ftp access on aws ec2 instance (debian 10)

	follow the instructions here: https://www.infiflex.com/how-to-configure-ftp-on-an-ec2-instance

	username:password = ftpuser:ftpuser

		```sh
		sudo apt install vsftpd
		```

	copy the original file`sudo cp /etc/vsftpd.conf /etc/vsftpd.conf.orig`


	add the ftp user`sudo adduser ftpuser`

	change their permissions:
		```sh
		sudo chown nobody:nogroup /home/ftpuser/ftp
		sudo chmod a-w /home/ftpuser/ftp
		```

	create the directories where files will be uploaded:
		```sh
		sudo mkdir /home/ftpuser/ftp/files
		sudo chown ftpuser:ftpuser /home/ftpuser/ftp/files
		```

	add or uncomment the following lines:
		```
		anonymous_enable=NO
		# Uncomment this to allow local users to log in.
		local_enable=YES
		write_enable=YES
		chroot_local_user=YES
		user_sub_token=$USER
		local_root=/home/$USER/ftp

		pasv_min_port=1024
		pasv_max_port=1048

		userlist_enable=YES
		userlist_file=/etc/vsftpd.userlist
		userlist_deny=NO
		pasv_address=<Public IP of your instance>
		```

		restart the service `sudo systemctl restart vsftpd`


issues connecting to RDS instance from EC2 instance (hint: use your private IP address when adding inbound traffic rules to security groups)
see:
https://stackoverflow.com/a/40078116/6158303


<name="create_shipping_event_type"></a>
12. ###### adding the ability to create shipping events

	within the `order-detail` page there is a dropdown labeled "Create shipping event" with a default option
	of "--choose event type --", and no other options

	in order to add additional options to that dropdown list, go to http://127.0.0.1:8000/admin/order/shippingeventtype/
	and add a shipping event type.


12. ###### adding more 'sites' to django
	go to http://127.0.0.1:8000/admin/sites/site/ and click 'ADD SITE'

	note: deleting the default site, which is normally 'example.com', does NOT screw anything up, but it may leave some `Order` objects without an attached `Site` object - the side effects to this remain uncertain, other than sending order related emails

	how to delete the default site: go into the admin site, find `Sites`, and delete the default/unused `Site` objects


	```py
	# setting.py
	...
	SITE_ID = 2
	...

	```

<name="create_oscar_email_template"></a>
12. ###### Adding the ability to create/customize an email template from the dashboard

	from: https://django-oscar.readthedocs.io/en/3.1/howto/how_to_customise_oscar_communications.html?highlight=email#customising-through-the-database

	for this example, we'll be adding the ORDER_PLACED communication event type to the dashboard,
	which is a preexisting event type within oscar

	1. go to /admin/communication/communicationeventtype/add/

	2. edit the fields using the following values:
		- Code: `ORDER_PLACED`
		- Name: `Order Placed`
		- Category: `Order related`
		- Email Subject Template: `{% load i18n %}{% blocktrans with order_number=order.number %}DEHY: We have received your order! ({{ order_number }}){% endblocktrans %}` - copy/pasted/modified version of: `templates/oscar/communication/emails/commtype_order_placed_subject.txt`
		- Email Body Template: copied the contents from `templates/oscar/communication/emails/commtype_order_placed_body.txt`
		- Email Body HTML:
			```html
			{% extends "oscar/communication/emails/base.html" %}
				{% load currency_filters i18n %}

				{% block tbody %}
				<tr>
				    <td align="center" class="content-block">
				     <table style="border-collapse:collapse; width:500px;" cellpadding="0" cellspacing="0">
					<tbody>
					    <tr>
						<td>
							<p xmlns="http://www.w3.org/1999/html">{% trans 'Hello,' %}</p>
				                        <p>{% blocktrans with order_number=order.number %}We are pleased to confirm your order {{ order_number }} has been received and will be processed shortly.{% endblocktrans %}</p>
						</td>
					</tr>
					</tbody>
					</table>
				    </td>
				</tr>

				<tr>
				    <td align="center" class="content-block">
				        {% include "oscar/communication/emails/order_info_table.html" %}
				    </td>
				</tr>

				<tr>
				    <td align="center" class="content-block">
				        {% include "oscar/communication/emails/order_contents_table.html" %}
				    </td>
				</tr>

				{% endblock %}
			```
		- SMS Template:

<name="adding_new_communication_event_type"></a>
12. ####### Adding a new/custom communication event type to Oscar in order to allow emails to be sent when an order has shipped

	This follows the instructions from the example in the previous section, except the event type we're
	adding does not come standard within Oscar

	1. go to /admin/communication/communicationeventtype/add/

	2. edit the fields using the following values:
		- Code: `ORDER_SHIPPED`
		- Name: `Order Shipped`
		- Category: `Order related`
		- Email Subject Template: `{% load i18n %}{% blocktrans with order_number=order.number %}  DEHY: Great news, your order has shipped! ({{ order_number }}) {% endblocktrans %}`
		- Email Body Template:
		- Email Body HTML:
			```html
				{% extends "oscar/communication/emails/orders_base.html" %}
				{% load currency_filters i18n %}

				{% block header %}
				{{block.super}}
				{% endblock header %}

				{% block body %}
				{{block.super}}
				{% endblock body %}
			```
		- SMS Template:

		- Code:
		- Name:
		- Email Subject Template:



<a name='custom_shipping_condition'></a>
12. ###### creating a custom conditional for specific shipping code and value requirement

	```py
		from oscar.apps.offer.custom import create_condition
		from dehy.appz.offer.custom import FreeFedexGroundShippingCondition
		from oscar.core.loading import get_class, get_model
		from decimal import Decimal as D

		Range = get_model('offer', 'Range')
		all_products_range = Range.objects.get(name='All Products')

		create_condition(FreeFedexGroundShippingCondition, value=50.00, range=all_products_range, type='Value')
	```


13. ###### implementing a custom benefit

	if haven't done yet, follow the instructions in the above step
	```py
		from oscar.core.loading import get_class, get_model
		from oscar.apps.offer.custom import create_benefit
		from dehy.appz.offer.custom import FreeFedexGroundShippingCondition, FreeGroundShippingBenefit
		Condition = get_model('offer', 'Condition')
		ConditionalOffer = get_model('offer', 'ConditionalOffer')
		Range = get_model('offer', 'Range')
		condition = Condition.objects.get(proxy_class='dehy.appz.offer.custom.FreeFedexGroundShippingCondition')
		ShippingPercentageDiscountBenefit = get_class('offer.benefits', 'ShippingPercentageDiscountBenefit')
		all_products_range = Range.objects.get(name='All Products')
		FreeGroundShippingBenefit = create_benefit(FreeGroundShippingBenefit, range=all_products_range, type='Shipping percentage', value=100)
		free_ground_shipping_offer,created = ConditionalOffer.objects.get_or_create(
			name='Ground shipping - FREE For Orders Over $50', condition=condition, offer_type="Site", benefit=FreeGroundShippingBenefit,
			max_basket_applications=1,
			defaults={'name':"FedEx Ground - FREE For Orders Over $50", 'offer_type':"Site", 'benefit':FreeGroundShippingBenefit,
				'max_basket_applications':1
			}
		)
	```

<a name="quickbooks_api_setup"></a>
1. ####### Quickbooks API setup

	- generate initial tokens via https://developer.intuit.com/app/developer/playground?code=AB11655164630b8uPwdL5WqHTsXzH4IdmQm0kR0RTltsh6eEyo&state=PlaygroundAuth&realmId=4620816365229458310

	- realm id can also be attained in the previous link, or from https://developer.intuit.com/app/developer/qbo/docs/api/accounting/most-commonly-used/account (the account dropdown near the top will have an account name and a large number next to it)

	```py
	from oscar.core.loading import get_model, get_class
	QB = get_model('generic', 'QuickbooksAuthToken')
	qb_auth_token,created = QB.objects.update_or_create(
		expires_in=3600, refresh_expires_in=8726400, realm_id=4620816365229458310,
		defaults={'expires_in':3600, 'realm_id':4620816365229458310,'refresh_expires_in':8726400, 'refresh_token': 'AB11664206361T35EVnpFD1aElG6H3qhIwvMo2DOhCpXbxpUdq', 'access_token':'eyJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..hVT23JqoEslENhnVKxnmSQ.2k5UlXuhIg3MGQFecRXAXSgwzlSPoFLkZmIAMNN5CQn29tuhUpEYzo4l5fzy2YUoLXXbTOH_o_D2UQIN5dbDcIObPytzhTmfG2No3WWV9V2gaxo2V0zOFS3fnrbiqB20yFzTjAV9WrKAZitF8krjAmdROJzfvUgcr-hhllcbbTj66fe32tGTVMdWr8JfbGSny2gmO90i9VNXEPBR_Huzy7bbNXZRafKtq-Y37Fowvlx_ZsVzqnRwmy_-gocASxGsiGOrSmyg0nW_XHPKxj-Z8Zy8rORQ_rzfrnrCszKfTzCJDk6QMCpu0PL6pktdXdpk8t6EHhKWvRvBZ_T3z21nfdh2zNHlINsSxT5mqX8LLYRDor8Kc4sbnAXaHpnlbRaRHSrA1h-8tLZvWkvCc-qvnpMX632gtDF76GpCNVefA61M76PDV2SIWdm34i2qn5qjtZoXtOI0k9Ra1hqZjpZ0lkx3WV1gH7qz1H6zGr8SVqdI8sCSmAQRLeVVvwwcDug94-8yRcUIA2-csE8HvaaRpvWhbUBFO_Ju-okoKqRjB8GKUntKd3pPxdcGIXb4qK5Ooq7AW9ykRLoaTVc17Qh7DoVxfObffun-NogQJJudwL_20cQ8okqsKg_CEOrb6Y0Fvz6HTkm2PjIQuOpVHtDfe2BSxajBGBRr_ZsR-MVshqErMXf-RR8YGCChYE3f0273ENBM3bL-w4JQF_ZNJAeKfqfniXC1ljdeSvDLY1ffvZgDAtjEdMuNiQAzUF-UsFZ4.xKbxulybew5WAEqftLpNZQ'
		}
	)

	qb_auth_token.save()
		```


<a name="celery_rabbitmq"></a>
1. ###### Installing celery and it's dependencies (rabbitMQ)

	guides:
		celery: https://docs.celeryq.dev/en/master/getting-started/first-steps-with-celery.html
		rabbitMQ: https://www.rabbitmq.com/install-debian.html#apt-quick-start-cloudsmith

	1. rabbitMQ installation:

		1. create a new file from the home directory on the remote server `nano rabbitmq_install_script.sh`
		2. save the following snippet to the file
		3. give the file execute permissions: `sudo chmod +x rabbitmq_install_script.sh`
		4. run the script: `./rabbitmq_install_script.sh`

			```
			#!/usr/bin/sh
			sudo apt-get install curl gnupg apt-transport-https -y

			## Team RabbitMQ's main signing key
			curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null
			## Cloudsmith: modern Erlang repository
			curl -1sLf https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/gpg.E495BB49CC4BBE5B.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg > /dev/null
			## Cloudsmith: RabbitMQ repository
			curl -1sLf https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/gpg.9F4587F226208342.key | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg > /dev/null
			## Add apt repositories maintained by Team RabbitMQ
			sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF

			## Provides modern Erlang/OTP releases
			deb [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/deb/ubuntu bionic main
			deb-src [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/deb/ubuntu bionic main

			## Provides RabbitMQ
			deb [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/deb/ubuntu bionic main
			deb-src [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/deb/ubuntu bionic main
			EOF

			## Update package indices
			sudo apt-get update -y

			## Install Erlang packages
			sudo apt-get install -y erlang-base \
			                        erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
			                        erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
			                        erlang-runtime-tools erlang-snmp erlang-ssl \
			                        erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

			## Install rabbitmq-server and its dependencies
			sudo apt-get install rabbitmq-server -y --fix-missing
			```

	2. [setting up rabbitmq](https://docs.celeryq.dev/en/master/getting-started/backends-and-brokers/rabbitmq.html#setting-up-rabbitmq):

		get the user,pass,and vhost names from .prod and replace them in the export line below
			```sh
			export RABBITMQ_USER=myuser && RABBITMQ_PASS=mypass && RABBITMQ_VHOST=myvhost
			sudo rabbitmqctl add_user $RABBITMQ_USER $RABBITMQ_PASS
			sudo rabbitmqctl add_vhost $RABBITMQ_VHOST
			sudo rabbitmqctl set_permissions -p $RABBITMQ_VHOST $RABBITMQ_USER ".*" ".*" ".*"
			```

		in `settings.py`, add the following line to configure the broker url using the settings created above:
		`CELERY_BROKER_URL = f"amqp://{env.str('RABBITMQ_USER')}:{env.str('RABBITMQ_PASS')}@localhost:5672/{env.str('RABBITMQ_VHOST')}"`

	3. installing celery:
		`pip install celery`

	4. setup celery:

			create celery config file `dehy/celery.py`, should be same directory as `settings.py`
			```py
			import os

			from celery import Celery

			# Set the default Django settings module for the 'celery' program.
			os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dehy.settings')

			app = Celery('dehy')

			# Using a string here means the worker doesn't have to serialize
			# the configuration object to child processes.
			# - namespace='CELERY' means all celery-related configuration keys
			#   should have a `CELERY_` prefix.
			app.config_from_object('django.conf:settings', namespace='CELERY')

			# Load task modules from all registered Django apps.
			app.autodiscover_tasks()


			@app.task(bind=True, ignore_result=True)
			def debug_task(self):
			    print(f'Request: {self.request!r}')
			```

			add the following to `dehy/__init__.py`, again, same directory as `settings.py`:

				```py
				from .celery import app as celery_app
				__all__ = ('celery_app',)
				```

	4. installing supervisor
		`sudo apt install supervisor`
		`pip install supervisor`

	5. daemonizing celery via supervisor

		1. Get configuration from the [Official Celery](https://raw.githubusercontent.com/celery/celery/master/extra/supervisord/celeryd.conf) and save it to supervisor's default file discovery folder:
			```
			$ cd /etc/supervisor/conf.d/
			$ sudo wget https://raw.githubusercontent.com/celery/celery/master/extra/supervisord/celeryd.conf
			$ ls
			celeryd.conf
			```

		2. Edit `command`, `directory` and `user` according to your project.
			```sh
			directory=/home/admin/dehy/dehy
			user=admin
			command=/home/admin/dehy/dehy/venv/bin/celery -A dehy worker --loglevel=info
			```

		3. Save


