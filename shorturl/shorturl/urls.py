from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'urldispatch.views.home', name='home'),
    # url(r'^urldispatch/', include('urldispatch.foo.urls')),

    url(r'^$', 'urldispatch.views.home', name='home'),
    url(r'^add$', 'urldispatch.views.add', name='add'),
    url(r'^items$', 'urldispatch.views.your_items', name='items'),
    url(r'^edit/(?P<short_url>[a-zA-Z0-9_-]+)$', 'urldispatch.views.edit_url', name='edit'),
    url(r'^urlcheck$', 'urldispatch.views.urlcheck', name='urlcheck'),
    url(r'^urlcheck/shortname/(?P<short_url>[a-zA-Z0-9_-]+)$', 'urldispatch.views.urlcheck_shortname', name='urlcheck_shortname'),
    url(r'^(?P<short_url>[a-zA-Z0-9_-]+)$', 'urldispatch.views.redirect', name='redirect'),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
