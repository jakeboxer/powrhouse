# This should run every hour
from autoassign.functions import *
from django.contrib.contenttypes.models import ContentType
from django.core.management import setup_environ
import datetime, MySQLdb, re, settings, time

setup_environ(settings)

if __name__ == "__main__":
    send_morning_digests()
    