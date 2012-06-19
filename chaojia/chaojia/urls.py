from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'chaojia.views.home', name='home'),
    # url(r'^chaojia/', include('chaojia.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    #(r'^weibo/',include('weibo.weiboUrl')),
    (r'^oauth/',include('chaojia.login.urls')),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',{ 'document_root': settings.STATIC_PATH+'/public/js' }),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',{ 'document_root': settings.STATIC_PATH+'/public/css' }),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',{ 'document_root': settings.STATIC_PATH+'/public/images' }),
)
