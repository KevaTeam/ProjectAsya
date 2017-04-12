from api.models import User
from api.helpers import *


def list_action(request):
    if not request.client.log_in:
        return not_logged_response()

    order = request.GET.get('order', False)

    users = User.objects.all()

    if order == 'rating':
        users = User.objects.raw('''
           SELECT
               u.*,
               MAX(uq.end) AS last_passed_quest
           FROM api_user AS u
               LEFT JOIN api_userquest AS uq ON (
                   uq.user_id = u.id AND
                   uq.end > 0
               )
           GROUP BY u.id
           ORDER BY u.rating DESC, last_passed_quest
           ''')

    array = []

    for user in users:
        u = user.to_list()

        if request.client.is_admin():
            u.update({
                'role': user.role,
                'activated': 1,
                'mail': user.mail
            })

        array.append(u)

    return success_response({
        'count': len(array),
        'items': array
    })


def get_action(request):
    pass


def delete_action(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    id = get_param_or_fail(request, 'id')

    try:
        user = User.objects.get(id=id)
        user.delete()

        return success_response('1')
    except User.DoesNotExist:
        return failure_response('User is not found')


def search_action(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    name = get_param_or_fail(request, 'name')

    if not name:
        return failure_response('Name is not defined')

    users = User.objects.all().filter(name__contains=name)

    array = []

    for user in users:
        array.append({
            'id': user.id,
            'name': user.name
        })

    return success_response(array)