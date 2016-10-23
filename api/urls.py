from django.conf.urls import include, url

from .methods import (
    auth as auth
)
from . import views

# from methods import
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^token$', auth.auth),

    url(r'^method/', include([
        url(r'^auth.signup$', auth.signup)
    ]))
]
