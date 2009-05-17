# Django settings for powr_local project.
import loc_settings as loc

DEBUG = loc.DEBUG
TEMPLATE_DEBUG = loc.TEMPLATE_DEBUG

ADMINS = loc.ADMINS

MANAGERS = loc.MANAGERS

DATABASE_ENGINE   = loc.DATABASE_ENGINE
DATABASE_NAME     = loc.DATABASE_NAME
DATABASE_USER     = loc.DATABASE_USER
DATABASE_PASSWORD = loc.DATABASE_PASSWORD
DATABASE_HOST     = loc.DATABASE_HOST
DATABASE_PORT     = loc.DATABASE_PORT

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = loc.TIME_ZONE

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = loc.LANGUAGE_CODE

SITE_ID = loc.SITE_ID

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = loc.USE_I18N

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = loc.MEDIA_ROOT

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = loc.MEDIA_URL

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = loc.ADMIN_MEDIA_PREFIX

# Make this unique, and don't share it with anybody.
SECRET_KEY = loc.SECRET_KEY

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = loc.TEMPLATE_LOADERS

MIDDLEWARE_CLASSES = loc.MIDDLEWARE_CLASSES

ROOT_URLCONF = loc.ROOT_URLCONF

TEMPLATE_DIRS = loc.TEMPLATE_DIRS

INSTALLED_APPS = loc.INSTALLED_APPS

TEMPLATE_CONTEXT_PROCESSORS = loc.TEMPLATE_CONTEXT_PROCESSORS

LOGIN_REDIRECT_URL = loc.LOGIN_REDIRECT_URL

EMAIL_HOST = loc.EMAIL_HOST
EMAIL_PORT = loc.EMAIL_PORT

# for django_registration
ACCOUNT_ACTIVATION_DAYS = loc.ACCOUNT_ACTIVATION_DAYS

# for django toolbar
INTERNAL_IPS = loc.INTERNAL_IPS
DEBUG_TOOLBAR_CONFIG = loc.DEBUG_TOOLBAR_CONFIG