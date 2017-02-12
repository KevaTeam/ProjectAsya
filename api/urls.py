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

        url(r'^category.', include([
            url(r'^add$', category.add),
            url(r'^list$', category.list),
            url(r'^edit$', category.edit),
            url(r'^delete$', category.delete)
        ])),

        url(r'^timer.get$', timer.get),

        url(r'^user.', include([
            url(r'^list$', user.list),
            url(r'^get$', user.get),
            url(r'^delete$', user.delete),
        ])),

        url(r'^quest.', include([
            url(r'^list$', quest.list_quest),
            url(r'^take$', quest.take_quest),
            url(r'^pass$', quest.pass_answer),
            url(r'^create$', quest.create_quest),
            url(r'^save$', quest.edit_quest),
            url(r'^delete$', quest.delete_quest),
            url(r'^attempts$', quest.get_attempts)
        ]))
    ]))
]
