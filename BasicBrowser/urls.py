from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^topic/(?P<topic_id>\d+)/$', 'tmv_app.views.topic_detail'),
    (r'^term/(?P<term_id>\d+)/$', 'tmv_app.views.term_detail'),
    (r'^doc/(?P<doc_id>\d+)/$', 'tmv_app.views.doc_detail'),
    (r'^topic_list$', 'tmv_app.views.topic_list_detail'),
    (r'^topic_presence$', 'tmv_app.views.topic_presence_detail'),
    (r'^stats$', 'tmv_app.views.stats'),
    (r'^settings$', 'tmv_app.views.settings'),
    (r'^settings/apply$', 'tmv_app.views.apply_settings'),
    (r'^topic/random$', 'tmv_app.views.topic_random'),
    (r'^doc/random$', 'tmv_app.views.doc_random'),
    (r'^term/random$', 'tmv_app.views.term_random'),
    # Example:
    # (r'^BasicBrowser/', include('BasicBrowser.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)


#onyl serve static content for development
urlpatterns += patterns('', (
r'^static/(?P<path>.*)$',
'django.views.static.serve',
{'document_root': 'static'}
))
