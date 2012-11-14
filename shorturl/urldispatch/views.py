from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST, require_safe

import datetime
import hashlib
import json
import math
import random

from decorators import *
from forms import EditForm
from models import Url
from utils import test_url, get_destination_url

@require_safe
@login_required
@render_to("home.html")
def home(request):
    return {}

def get_unique_id(url, username):
    """ Return new (saved) Url object with unique short URL """
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
            obj = Url.objects.create(short_url=short_url, short_name=short_url, username=username, destination_url=url)
            obj.save()
            return obj
        except IntegrityError:
            iteration += 1

@require_http_methods(["GET", "POST", "HEAD"])
@login_required
@render_to("edit.html")
def edit_url(request, short_url):
    username = request.user.username

    # Validation & authorization
    object = get_object_or_404(Url, short_url=short_url)
    if object.username != username:
        raise PermissionDenied("That's not your item")

    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
           short_name = slugify(form.cleaned_data["short_name"])
           short_name_count = Url.objects.filter(short_name=short_name).count()
           short_url_count = Url.objects.filter(short_url=short_name).count()

           if short_name in settings.RESERVED_URLS:
               errors = form._errors.setdefault("short_name", ErrorList())
               errors.append("That URL is reserved")
           elif short_name != object.short_url and len(short_name) < 7:
               errors = form._errors.setdefault("short_name", ErrorList())
               errors.append("That's too short (<7 characters)")
           elif (short_name != object.short_name and short_name_count > 0) or (short_name != object.short_url and short_url_count > 0):
               errors = form._errors.setdefault("short_name", ErrorList())
               errors.append("Sorry! That URL already exists")
           else:
               object.short_name = short_name
               object.active = form.cleaned_data["active"]
               object.save()

               # Form contents changed - recreate it to update page.
               form = EditForm({"short_name": object.short_name, "active": object.active})
    else:
        form = EditForm({"short_name": object.short_name, "active": object.active})

    return {"item": object, "form": form, "short_url": short_url}

@require_POST
@login_required
@csrf_exempt
@ajax_request
def urlcheck(request):
    url = request.POST.get("long_url", None)
    if not url:
        return { "valid": False }
    status = test_url(get_destination_url(url))
    if status["status_current"]:
        return { "valid": True }
    return { "valid": False }


@require_POST
@login_required
@csrf_exempt
@ajax_request
def add(request):
    username = request.user.username
    url = request.POST.get("long_url")
    if not url:
        return {"success": False, "message": "Invalid URL"}

    try:
        obj = Url.objects.get(destination_url=url)
    except:
        obj = get_unique_id(url, username)

    return {"success": True, "url": "http://%s/%s" % (settings.SHORTURL_DOMAIN, obj.short_url), "edit_url": "/edit/%s" % obj.short_url }

@require_safe
def redirect(request, short_url):
    item = get_object_or_404(Url, short_url=short_url)
    if not item.active:
        raise Http404
    item.last_access = now()
    item.view_count += 1
    item.save()
    return HttpResponseRedirect(item.get_destination_url())

@require_safe
@render_to("your_items.html")
def your_items(request):
    username = request.user.username
    items = Url.objects.filter(username=username).filter(active=True)
    return {"items": items}
