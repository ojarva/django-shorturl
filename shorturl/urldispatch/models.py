from django.db import models
from django.conf import settings
import urllib2
from django.utils.timezone import now


class Url(models.Model):
    short_url = models.CharField(max_length=50,primary_key=True)
    short_name = models.CharField(max_length=50,unique=True,null=True,blank=True)
    owner = models.CharField(max_length=50)
    destination_url = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    last_access = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    last_working = models.DateTimeField(null=True, blank=True)
    last_fail = models.DateTimeField(null=True, blank=True)
    last_status = models.BooleanField(default=False)
    last_error = models.TextField(null=True, blank=True)
    fail_count = models.IntegerField(default=0)

    class Meta:
        get_latest_by = "created"
        ordering = ["-created", "-modified"]

    def get_short_url(self):
        return "https://%s/%s" % (settings.SHORTURL_DOMAIN, self.short_name)

    def test_url(self, dry_run=False):
        def fail(message):
            self.last_fail = now()
            self.fail_count += 1
            self.last_status = False
            self.last_error = message
            self.save()

        def success():
            self.last_working = now()
            self.last_status = True
            self.save()

        class HeadRequest(urllib2.Request):
            def get_method(self):
                return "HEAD"

        try:
            a = urllib2.urlopen(HeadRequest(self.destination_url))
            headers = dict(a.info())
            success()
        except urllib2.HTTPError, err:
            fail(str(err))
        except urllib2.URLError, err:
            fail(str(err))
