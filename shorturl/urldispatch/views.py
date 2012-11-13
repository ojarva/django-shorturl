from django.forms.util import ErrorList
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.timezone import now
import datetime
import json
import hashlib
import random
import math

from models import Url
from forms import EditForm

def home(request):
    return render_to_response("home.html", {}, context_instance=RequestContext(request))

def get_unique_id(url, username):
    iteration = 0
    hdigest = "%s-%s" % (url, random.random())
    while True:
        hdigest = hashlib.sha512(hdigest).hexdigest()
        if iteration < 10:
            short_url = hdigest[0:4]
        else:
            length = 4 + int(math.sqrt(iteration - 10))
        if iteration == 100:
            raise Exception("Can't find unique shorturl")
        try:
            obj = Url.objects.create(short_url=short_url, short_name=short_url, owner=username, destination_url=url)
            obj.save()
            return obj
        except IOError:
            iteration += 1

def edit_url(request, short_url):
    username = "test"
    object = get_object_or_404(Url, short_url=short_url)
    if object.owner != username:
        raise PermissionDenied("That's not your item")

    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
           short_name = slugify(form.cleaned_data["short_name"])
           short_name_count = Url.objects.filter(short_name=short_name).count()
           short_url_count = Url.objects.filter(short_url=short_name).count()

           if short_name in settings.RESERVED_URLS:
               errors = form._errors.setdefault("short_name", ErrorList())
               errors.append("Your short URL is reserved.")
           elif short_name != object.short_url and len(short_name) < 5:
               errors = form._errors.setdefault("short_name", ErrorList())
               errors.append("That's too short (<5 characters)")
           elif (short_name != object.short_name and short_name_count > 0) or (short_name != object.short_url and short_url_count > 0):
               errors = form._errors.setdefault("short_name", ErrorList())
               errors.append("Sorry! Your short URL already exists")
           else:
               object.short_name = short_name
               object.deleted = form.cleaned_data["deleted"]
               object.save()
               form = EditForm({"short_name": object.short_name, "deleted": object.deleted})
    else:
        form = EditForm({"short_name": object.short_name, "deleted": object.deleted})

    return render_to_response("edit.html", {"form": form, "short_url": short_url}, context_instance=RequestContext(request))

@csrf_exempt
def add(request):
    username = "test"
    if request.method == 'POST':
        url = request.POST.get("long_url")
        if not url:
            return HttpResponse(json.dumps({"success": False, "message": "Invalid URL"}))
        obj = get_unique_id(url, username)
        return HttpResponse(json.dumps({"success": True, "url": "http://%s/%s" % (settings.SHORTURL_DOMAIN, obj.short_url)}))
        
    return HttpResponse(json.dumps({"success": False, "message": "Invalid request"}))

def redirect(request, short_url):
    item = get_object_or_404(Url, short_url=short_url)
    item.last_access = now()
    item.views += 1
    item.save()
    return HttpResponseRedirect(item.destination_url)

def your_items(request):
    username = "test"
    items = Url.objects.filter(owner=username)
    return render_to_response("your_items.html", {"items": items}, context_instance=RequestContext(request))

