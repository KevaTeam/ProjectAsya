from datetime import datetime
from api.models import Message, User
from api.helpers import success_response, failure_response, get_param_or_fail, not_logged_response

MESSAGE_TYPES = {
    'all': 1,
    'individual': 2
}


def list_action(request):
    if not request.client.log_in:
        return not_logged_response()

    messages = Message.objects.raw('SELECT m.*, u.name FROM api_message AS m LEFT JOIN api_user AS u ON m.user = u.id')

    items = []
    for m in messages:
        items.append({
            'id': m.id,
            'title': m.title,
            'text': m.text,
            'type': m.type,
            'time': m.time,
            'user': {
                'id': m.user,
                'name': m.name
            }
        })

    return success_response({
        'items': items
    })


def add_action(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")
    try:
        title = get_param_or_fail(request, 'title')
        text = get_param_or_fail(request, 'text')
        type = get_param_or_fail(request, 'type')
        user = get_param_or_fail(request, 'user', is_required=False)
        time = datetime.now()

        if user and int(type) == MESSAGE_TYPES['individual']:
            user = User.objects.get(id=user)
            user_id = user.id
        else:
            user_id = 0

        message = Message(title=title, type=type, text=text, time=time, user=user_id)

        message.save()
    except User.DoesNotExist as e:
        return failure_response('User is not found')
    except Exception as e:
        return failure_response(e.args[0])

    return success_response(message.id)


def edit_action(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    try:
        id = get_param_or_fail(request, 'id')
        title = get_param_or_fail(request, 'title')
        text = get_param_or_fail(request, 'text')
        type = get_param_or_fail(request, 'type')
        user = get_param_or_fail(request, 'user', is_required=False)
        time = datetime.now()

        if user and int(type) == MESSAGE_TYPES['individual']:
            user = User.objects.get(id=user)
            user_id = user.id
        else:
            user_id = 0
        message = Message.objects.get(id=id)

        message.title = title
        message.text = text
        message.type = type
        message.time = time
        message.user = user_id

        message.save()
    except Message.DoesNotExist:
        return failure_response("Message with this id is not exists")
    except User.DoesNotExist:
        return failure_response("User with this id is not exists")
    except Exception as e:
        return failure_response(e.args[0])

    return success_response(message.id)


def delete_action(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    try:
        id = get_param_or_fail(request, 'id')

        quest = Message.objects.get(id=id)
        quest.delete()

        return success_response('1')
    except Message.DoesNotExist:
        return failure_response('Quest is not found')
    except Exception as e:
        return failure_response(e.args[0])