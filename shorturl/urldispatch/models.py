from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.timezone import now

import urllib2
import socket

from urlparse import urlparse
from utils import test_url, get_destination_url


class Url(models.Model):
    username = models.CharField(max_length=50)

    short_url = models.CharField(max_length=50,primary_key=True)
    short_name = models.CharField(max_length=50,unique=True,null=True,blank=True)
    destination_url = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)
    last_access = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)

    status_last_working = models.DateTimeField(null=True, blank=True, help_text="Last time url was accessible")
    status_working_since = models.DateTimeField(null=True, blank=True, help_text="URL has been accessible from this date")
    status_last_fail = models.DateTimeField(null=True, blank=True, help_text="Last time URL was not accessible")
    status_current = models.BooleanField(default=False, help_text="Current status")
    status_last_error = models.TextField(null=True, blank=True, help_text="Last error message")
    status_fail_count = models.IntegerField(default=0, help_text="Number of failures")

    class Meta:
        get_latest_by = "created"
        ordering = ["-created", "-modified"]

    def get_short_name(self):
        return "https://%s/%s" % (settings.SHORTURL_DOMAIN, self.short_name)

    def get_short_url(self):
        return "https://%s/%s" % (settings.SHORTURL_DOMAIN, self.short_url)

    def get_destination_url(self):
        return get_destination_url(self.destination_url)

    def test_url(self):
        data = test_url(self.get_destination_url())

        def fail(message):
            self.status_working_since = None
            self.status_last_fail = now()
            self.status_fail_count += 1
            self.status_current = False
            self.status_last_error = message
            self.save()

        def success():
            if self.status_current == False:
                self.status_working_since = now()
            self.status_last_working = now()
            self.status_current = True
            self.save()

        if data["status_current"]:
            success()
        else:
            fail(data["status_last_error"])

        for item in ["status_fail_count", "status_current", "status_last_error", "status_last_working", "status_last_fail", "status_working_since"]:
            data[item] = getattr(self, item)
        return data

    def validate_short_name(self, url, save=False):
        short_name = slugify(url)
        short_name_count = Url.objects.filter(short_name=short_name).count()
        short_url_count = Url.objects.filter(short_url=short_name).count()

        if short_name in settings.RESERVED_URLS:
            return "That URL is reserved"
        elif short_name != self.short_url and len(short_name) < 7:
            return "That's too short (<7 characters)"
        elif (short_name != self.short_name and short_name_count > 0) or (short_name != self.short_url and short_url_count > 0):
            return "Sorry! That URL already exists"
        else:
            if save:
                self.short_name = short_name
                self.save()
            return True
