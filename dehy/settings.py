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

ENV_FILE = '.env'
if Repository('.').head.shorthand is 'main':
	ENV_FILE = '.env-prod'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)
environ.Env.read_env()

# env.read_env(env.str(BASE_DIR, '.env'))
env.read_env(BASE_DIR / ENV_FILE)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'dehy',
	# oscar overrides
	'dehy.appz.catalogue.apps.CatalogueConfig',
	'dehy.appz.dashboard.apps.DashboardConfig',
	'dehy.appz.dashboard.catalogue.apps.CatalogueDashboardConfig',
	'dehy.appz.basket.apps.BasketConfig',
	'dehy.appz.search.apps.SearchConfig',
	'dehy.appz.customer.apps.CustomerConfig',
	'dehy.appz.checkout.apps.CheckoutConfig',
	# django apps added by oscar
	'django.contrib.sites',
	'django.contrib.flatpages',
	# oscar apps
	'oscar.config.Shop',
	'oscar.apps.analytics.apps.AnalyticsConfig',
	'oscar.apps.address.apps.AddressConfig',
	'oscar.apps.shipping.apps.ShippingConfig',
	'oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig',
	'oscar.apps.communication.apps.CommunicationConfig',
	'oscar.apps.partner.apps.PartnerConfig',
	'oscar.apps.payment.apps.PaymentConfig',
	'oscar.apps.offer.apps.OfferConfig',
	'oscar.apps.order.apps.OrderConfig',
	'oscar.apps.voucher.apps.VoucherConfig',
	'oscar.apps.wishlists.apps.WishlistsConfig',
	'oscar.apps.dashboard.reports.apps.ReportsDashboardConfig',
	'oscar.apps.dashboard.users.apps.UsersDashboardConfig',
	'oscar.apps.dashboard.orders.apps.OrdersDashboardConfig',
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

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'oscar.apps.basket.middleware.BasketMiddleware',
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
	'default': env.db('DATABASE_URL')
    # read os.environ['DATABASE_URL'] and raises
    # ImproperlyConfigured exception if not found
    #
    # The db() method is an alias for db_url().
    # 'default': env.db(),
	#
    # read os.environ['SQLITE_URL']
    # 'extra': env.db_url(
    #     'SQLITE_URL',
    #     default='sqlite:////tmp/my-tmp-sqlite.db'
    # )
}
if DEBUG:

	CACHES = {
	    'default': {
	        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
	   }
	}
	MIDDLEWARE += ['dehy.middleware.DisableBrowserCacheMiddleware']

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'
# STATICFILES_DIRS = [BASE_DIR / 'static']

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

OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
	'Pending': ('Being processed', 'Cancelled',),
	'Being processed': ('Processed', 'Cancelled',),
	'Cancelled': (),
}

OSCAR_ORDER_STATUS_CASCADE = {
	'Being processed': 'In progress'
}

OSCAR_DEFAULT_CURRENCY = 'USD'
OSCAR_HIDDEN_FEATURES = ["reviews"]
OSCAR_HOMEPAGE = reverse_lazy('home')
OSCAR_SHOP_NAME = "DEHY"
OSCAR_SHOP_TAGLINE = ""