from django.conf.urls import include, url

from . import views

# from methods import
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admin/$', views.admin, name='admin')
]
