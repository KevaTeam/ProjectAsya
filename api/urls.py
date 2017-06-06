from django.conf.urls import include, url
from .methods import (
    auth as auth,
    category as category,
    check as check,
    message as message,
    timer as timer,
    user as user,
    quest as quest,
    rating as rating
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
            url(r'^add$', category.add_action),
            url(r'^list$', category.list_action),
            url(r'^edit$', category.edit_action),
            url(r'^delete$', category.delete_action)
        ])),

        url(r'^message.', include([
            url(r'^add$', message.add_action),
            url(r'^list$', message.list_action),
            url(r'^edit$', message.edit_action),
            url(r'^delete$', message.delete_action)
        ])),

        url(r'^timer.', include([
            url(r'^get$', timer.get_action),
            url(r'^set$', timer.set_action),
            url(r'^current$', timer.current_action),
        ])),

        url(r'^user.', include([
            url(r'^list$', user.list_action),
            url(r'^get$', user.get_action),
            url(r'^delete$', user.delete_action),
            url(r'^search$', user.search_action)
        ])),

        url(r'^quest.', include([
            url(r'^list$', quest.list_quest),
            url(r'^take$', quest.take_quest),
            url(r'^pass$', quest.pass_answer),
            url(r'^create$', quest.create_quest),
            url(r'^save$', quest.edit_quest),
            url(r'^delete$', quest.delete_quest),
            url(r'^attempts$', quest.get_attempts),
            url(r'^upload$', quest.upload_action)
        ])),

        url(r'^rating.', include([
            url(r'^list$', rating.list_action),
        ]))
    ]))
]
