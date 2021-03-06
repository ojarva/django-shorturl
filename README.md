django-shorturl
===============

This is minimal URL shortening service built on Django.

* Automatic URL generation
* Usage statistics (view counts)
* Custom URLs
* Fixes most commong copy-paste errors (missing protocol scheme, missing "h" from http" etc.)

Installation and requirements
-----------------------------

* Separate domain (/hostname). Configure to shorturl/local_settings.py:SHORTURL_DOMAIN
* Configure basic authentication (or any basic authentication compatible) to your web server. Alternatively, disable remote user middleware from settings.py (and configure models based authentication)
* Django >1.4, sqlite or other database
* Standard Django WSGI deployment, https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
* Add "manage.py check_urls" to cron (once per hour or so)
* Remember to run 

```
./manage.py syncdb
./manage.py collectstatic
```
