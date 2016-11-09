from api.models import User
from api.helpers import success_response, not_logged_response


def list(request):
    if not request.client.log_in:
        return not_logged_response()

    order = request.GET.get('order', False)

    if order != 'rating':
        order = '?'

    users = User.objects.all().order_by(order)
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
        'count': len(users),
        'items': array
    })

def get(request):
    pass

def delete(request):
    pass