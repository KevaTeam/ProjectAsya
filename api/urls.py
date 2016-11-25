from django.conf.urls import include, url

from .methods import (
    auth as auth,
    timer as timer,
    user as user,
    quest as quest,
    check as check,
    category as category
)
from . import views

# from methods import
urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^token$', auth.auth),

    url(r'^method/', include([
        url(r'^auth.signup$', auth.signup),

        url(r'^check.permission$', check.permission),

        url(r'^category.list$', category.list),

        url(r'^timer.get$', timer.get),

        url(r'^user.list$', user.list),
        url(r'^user.get$', user.get),
        url(r'^user.delete$', user.delete),

        url(r'^quest.list$', quest.list_quest),
        url(r'^quest.take$', quest.take_quest),
        url(r'^quest.pass$', quest.pass_answer),
        url(r'^quest.create$', quest.create_quest),
        url(r'^quest.save$', quest.edit_quest),
        url(r'^quest.delete$', quest.delete_quest),
        url(r'^quest.attempts$', quest.get_attempts),
    ]))
]
