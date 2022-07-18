"""
Django settings for dehy project
Django 3.2.11
https://docs.djangoproject.com/en/3.2/ref/settings/

django-oscar 3.1
https://django-oscar.readthedocs.io/en/3.1/ref/settings.html
"""
from oscar.defaults import *
import environ
from pathlib import Path
from pygit2 import Repository
from django.utils.translation import gettext_lazy as _
import logging
from sorl.thumbnail.log import ThumbnailLogHandler
from celery.schedules import crontab

ENV_FILE = '.env-prod' if Repository('.').head.shorthand == 'main' else '.env'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

ENV_FILE_LOCATION = BASE_DIR / ENV_FILE

BASE_DIR = BASE_DIR.parent

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)

env.read_env(str(ENV_FILE_LOCATION))
# env.read_env(BASE_DIR / ENV_FILE)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

SECRET_KEY = env.str('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=True)

BASE_URL = "https://www.dehygarnish.net"
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
INTERNAL_IPS = [
	"127.0.0.1"
]
# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.sitemaps',
	'django.contrib.postgres',
	'django_celery_beat',
	'dehy',
	'dehy.appz.generic.apps.GenericConfig',
	'dehy.appz.recipes.apps.RecipesConfig',
	'dehy.appz.wholesale.apps.WholesaleConfig',
	'dehy.appz.dashboard.recipes.apps.RecipesDashboardConfig',
	'dehy.appz.dashboard.faq.apps.FAQDashboardConfig',
	# oscar overrides
	'dehy.appz.address.apps.AddressConfig',
	'dehy.appz.dashboard.apps.DashboardConfig',
	'dehy.appz.dashboard.catalogue.apps.CatalogueDashboardConfig',
	'dehy.appz.dashboard.orders.apps.OrdersDashboardConfig',
	'dehy.appz.dashboard.reports.apps.ReportsDashboardConfig',
	'dehy.appz.basket.apps.BasketConfig',
	'dehy.appz.search.apps.SearchConfig',
	'dehy.appz.customer.apps.CustomerConfig',
	'dehy.appz.checkout.apps.CheckoutConfig',
	'dehy.appz.order.apps.OrderConfig',
	'dehy.appz.partner.apps.PartnerConfig',
	'dehy.appz.payment.apps.PaymentConfig',
	'dehy.appz.shipping.apps.ShippingConfig',
	# django apps added by oscar
	'django.contrib.sites',
	'django.contrib.flatpages',
	# oscar apps
	'oscar.config.Shop',
	'oscar.apps.analytics.apps.AnalyticsConfig',
	'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
	'oscar.apps.communication.apps.CommunicationConfig',
	'oscar.apps.offer.apps.OfferConfig',
	'oscar.apps.voucher.apps.VoucherConfig',
	'oscar.apps.wishlists.apps.WishlistsConfig',
	'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
	'oscar.apps.dashboard.offers.apps.OffersDashboardConfig',
	'oscar.apps.dashboard.partners.apps.PartnersDashboardConfig',
	'oscar.apps.dashboard.pages.apps.PagesDashboardConfig',
	'oscar.apps.dashboard.ranges.apps.RangesDashboardConfig',
	'oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig',
	'oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig',
	'oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig',
	'oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig',
	'dehy.appz.catalogue.apps.CatalogueConfig',
	# 3rd-party apps that oscar depends on
	'widget_tweaks',
	'haystack',
	'treebeard',
	'sorl.thumbnail',   # Default thumbnail backend, can be replaced
	'django_tables2',
	# other 3rd-party apps
	'django_better_admin_arrayfield',
	'django_ses',
]


SITE_ID = env.int('SITE_ID')

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'dehy.appz.basket.middleware.BasketMiddleware',
	'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'dehy.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'dehy.context_processors.add_ig_images_to_context',
				'dehy.context_processors.add_upsell_messages',
				'dehy.context_processors.basket_contents',
				'dehy.context_processors.order_total',
				'dehy.context_processors.add_recaptcha_site_keys',
				'dehy.context_processors.add_notifications',
				'oscar.apps.search.context_processors.search_form',
				'oscar.apps.checkout.context_processors.checkout',
				'oscar.apps.communication.notifications.context_processors.notifications',
				'oscar.core.context_processors.metadata',
			],
		},
	},
]

WSGI_APPLICATION = 'dehy.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Parse database connection url strings
# like psql://user:pass@127.0.0.1:8458/db
DATABASES = {
	# 'default': env.db('DATABASE_URL'),
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'USER': env.str('DB_USER'),
		'NAME': env.str('DB_NAME'),
		'PASSWORD': env.str('DB_PASS'),
		'HOST': env.str('DB_HOST'),
		'PORT': env.str('DB_PORT'),
		'ATOMIC_REQUESTS': True,
		'TEST': {
			'NAME': 'test_db',
		},
	}
}

# if DEBUG:
#
# 	INSTALLED_APPS += [
# 		'sslserver',
# 		'debug_toolbar'
# 	]
#
# 	MIDDLEWARE += [
# 		"debug_toolbar.middleware.DebugToolbarMiddleware",
# 	]
# 	DEBUG_TOOLBAR_CONFIG = {
#     	'SHOW_TEMPLATE_CONTEXT': True,
# 	}

	# CACHES = {
	#     'default': {
	#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
	#    }
	# }
	# MIDDLEWARE += ['dehy.middleware.DisableBrowserCacheMiddleware']

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

handler = ThumbnailLogHandler()
handler.setLevel(logging.CRITICAL)
logging.getLogger('sorl.thumbnail').addHandler(handler)

if not DEBUG:


	LOGGING = {
		'version': 1,
		'disable_existing_loggers': False,
		'handlers': {
			'file': {
				'level': 'DEBUG',
				'class': 'logging.FileHandler',
				'filename': 'logs/django.log',
			},
		},
		'loggers': {
			'django': {
				'handlers': ['file'],
				'level': 'DEBUG',
				'propagate': True,
			},
			'django.request': {
				'handlers': ['file'],
				'level': 'DEBUG',
				'propagate': True,
			}
		},
	}

# if DEBUG:
# 	LOGGING['handlers']['file']['level'] = 'DEBUG'
# 	LOGGING['loggers']['django']['level'] = 'DEBUG'
# 	LOGGING['loggers']['django.request']['level'] = 'DEBUG'
#

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
SITE_DOMAIN = 'dehygarnish.net'
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'us-east-2'
AWS_SES_REGION_ENDPOINT = 'email.us-east-2.amazonaws.com'
AWS_SES_ACCESS_KEY_ID = env.str('AWS_SES_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = env.str('AWS_SES_SECRET_ACCESS_KEY')
OSCAR_FROM_EMAIL = f'mail@{SITE_DOMAIN}'
AUTO_REPLY_EMAIL_ADDRESS = f'no-reply@{SITE_DOMAIN}'

OSCAR_GOOGLE_ANALYTICS_ID = 'G-W6L54G8SQ1'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = CELERY_TIMEZONE = 'America/Chicago'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGOUT_REDIRECT_URL = reverse_lazy('customer:login')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
# STATICFILES_DIRS = [BASE_DIR / 'assets']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
	'oscar.apps.customer.auth_backends.EmailBackend',
	'django.contrib.auth.backends.ModelBackend',
]

HAYSTACK_CONNECTIONS = {
	'default': {
		'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
	},
}

AUTH_USER_MODEL = "generic.User"
OSCAR_SEND_REGISTRATION_EMAIL = False
OSCAR_ALLOW_ANON_CHECKOUT = True
OSCAR_INITIAL_ORDER_STATUS = OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = OSCAR_LINE_STATUS_PIPELINE = {
	'Pending': ('Processed', 'Cancelled',),
	'Processed': ('Shipped', 'Cancelled',),
	'Shipped': ('Delivered', 'Cancelled',),
	'Delivered': (),
	'Cancelled': (),
}

OSCAR_ORDER_STATUS_CASCADE = {

	'Processed': 'Processed',
	'Shipped': 'Shipped',
	'Delivered': 'Delivered',
	'Cancelled': 'Cancelled'
}


OSCAR_ACCOUNTS_REDIRECT_URL = LOGIN_REDIRECT_URL = 'customer:profile-update'
OSCAR_DEFAULT_CURRENCY = 'USD'

OSCAR_COOKIES_DELETE_ON_LOGOUT = ['oscar_recently_viewed_products', 'oscar_open_basket']
OSCAR_HIDDEN_FEATURES = ["reviews", "wishlists"]
OSCAR_HOMEPAGE = reverse_lazy('catalogue:index')
OSCAR_SHOP_NAME = "DEHY"
OSCAR_SHOP_TAGLINE = ""
OSCAR_MISSING_IMAGE_URL = MEDIA_ROOT / "image_not_found.jpg"  # relative path from media root
OSCAR_REQUIRED_ADDRESS_FIELDS = ('first_name', 'last_name', 'line1', 'line4', 'postcode', 'country')
OSCAR_PRODUCTS_PER_PAGE = 10

OSCAR_THUMBNAIL_DEBUG = THUMBNAIL_DEBUG = DEBUG

OSCAR_DASHBOARD_NAVIGATION += [
	{
		'label': _('Recipe'),
		'icon': 'fas fa-bullhorn',
		'children': [
			{
				'label': _('Recipes'),
				'url_name': 'dashboard:recipe-list',
			},
		 ]
	},
	{
		'label': _('FAQ'),
		'icon': 'fas fa-bullhorn',
		'children': [
			{
				'label': _('FAQs'),
				'url_name': 'dashboard:faq-list',
			},
		 ]
	},
]

OSCAR_IMAGE_FOLDER = 'images/products'

STRIPE_SECRET_KEY = env.str('STRIPE_API_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = env.str('STRIPE_API_PUBLISHABLE_KEY')
STRIPE_CURRENCY = "USD"
STRIPE_ORDER_SUBMITTED_SIGNING_SECRET = env.str('STRIPE_ORDER_SUBMITTED_SIGNING_SECRET')

SHIPSTATION_API_KEY=env.str('SHIPSTATION_API_KEY')
SHIPSTATION_SECRET_KEY=env.str('SHIPSTATION_SECRET_KEY')

DEHY_SHIPSTATION_API_KEY = env.str('DEHY_SHIPSTATION_API_KEY')
DEHY_SHIPSTATION_SECRET_KEY = env.str('DEHY_SHIPSTATION_SECRET_KEY')

HOME_POSTCODE = "78701"
FREE_SHIPPING_AMOUNT = 50

FEDEX_ACCOUNT_NUMBER = env.str('FEDEX_ACCOUNT_NUMBER') if DEBUG else env.str('FEDEX_PRODUCTION_ACCOUNT_NUMBER')
FEDEX_API_KEY = env.str('FEDEX_TEST_API_KEY') if DEBUG else env.str('FEDEX_PRODUCTION_API_KEY')
FEDEX_SECRET_KEY = env.str('FEDEX_TEST_SECRET_KEY') if DEBUG else env.str('FEDEX_PRODUCTION_SECRET_KEY')
FEDEX_API_URL = env.str('FEDEX_TEST_API_URL') if DEBUG else env.str('FEDEX_PRODUCTION_API_URL')
USPS_USERNAME = env.str('USPS_USERNAME')

GOOGLE_RECAPTCHA_V2_SITE_KEY = env.str('GOOGLE_RECAPTCHA_V2_SITE_KEY')
GOOGLE_RECAPTCHA_V2_SECRET_KEY = env.str('GOOGLE_RECAPTCHA_V2_SECRET_KEY')
GOOGLE_RECAPTCHA_V3_SITE_KEY = env.str('GOOGLE_RECAPTCHA_V3_SITE_KEY')
GOOGLE_RECAPTCHA_V3_SECRET_KEY = env.str('GOOGLE_RECAPTCHA_V3_SECRET_KEY')

QUICKBOOKS_API_KEY = env.str('QUICKBOOKS_DEV_API_KEY')
QUICKBOOKS_SECRET_KEY = env.str('QUICKBOOKS_DEV_SECRET_KEY')
QUICKBOOKS_DISCOVERY_DOCUMENT_URL = env.str('QUICKBOOKS_DEV_DISCOVERY_DOCUMENT_URL')
QUICKBOOKS_ACCOUNTING_SCOPE = 'com.intuit.quickbooks.accounting'

QUICKBOOKS_BASE_URL = env.str('QUICKBOOKS_DEV_BASE_URL')
QUICKBOOKS_REDIRECT_URI = env.str('QUICKBOOKS_DEV_REDIRECT_URI')
QUICKBOOKS_ENVIRONMENT = 'sandbox'

QUICKBOOKS_REALM_ID = env.str('QUICKBOOKS_REALM_ID')

CELERY_BROKER_URL = f"amqp://{env.str('RABBITMQ_USER')}:{env.str('RABBITMQ_PASS')}@localhost:5672/{env.str('RABBITMQ_VHOST')}"
CELERY_BEAT_SCHEDULE = {
	'fedex-auth-token-every-5-minutes': {
        'task': 'dehy.tasks.update_fedex_auth_token',
        'schedule': crontab(minute='*/5'),
    },
	'quickbooks-auth-token-every-5-minutes': {
        'task': 'dehy.tasks.update_quickbooks_auth_token',
        'schedule': crontab(minute='*/5'),
    },
}