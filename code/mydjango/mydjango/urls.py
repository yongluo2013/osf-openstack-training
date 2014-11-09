from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mydjango.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    #url(r'^blog/index/\d{2}/$', "blog.views.index"),
    #url(r'^blog/index/(?P<id>\d{2})/$', "blog.views.index"),
    url(r'^blog/index/$', "blog.views.index"),
    url(r'^blog/regester/$', "blog.views.regester"),
   
)
