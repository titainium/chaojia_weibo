from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'chaojiame.views.home', name='home'),
     url(r'start', 'chaojia.login.views.home'),
     url(r'login', 'chaojia.login.views.use_sina_login'),
     url(r'sina$','chaojia.login.views.sina_login_suc'),
     url(r'test', 'chaojia.login.views.fortest'),
     #url(r'suc', 'iweibo8.login.views.sina_login_suc'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
