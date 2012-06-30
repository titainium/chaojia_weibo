from django.conf.urls.defaults import patterns, include

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bwsport.views.home', name='home'),
    # url(r'^bwsport/', include('bwsport.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^$','weibo.views.weibo_home'),
    (r'tags/$','weibo.views.weibo_tags'),
    (r'qzf/$','weibo.views.qzf'),
    (r'qzf/choose/$','weibo.views.choose_weibo_qzf'),
    (r'zf/choose/$','weibo.views.zf_choose'),
    (r'zf/weibo/$','weibo.views.zf_weibo'),
)
