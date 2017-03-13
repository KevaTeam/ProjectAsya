from datetime import datetime
from api.models import Message
from api.helpers import success_response, failure_response, get_param_or_fail, not_logged_response


def list(request):
    if not request.client.log_in:
        return not_logged_response()

    messages = Message.objects.values()

    return success_response({
        'items': [entry for entry in messages]
    })


def add(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    title = get_param_or_fail(request, 'title')
    text = get_param_or_fail(request, 'text')
    type = get_param_or_fail(request, 'type')

    time = datetime.now()

    try:
        message = Message(title=title, type=type, text=text, time=time)

        message.save()
    except Exception as e:
        return failure_response(e.args[0])

    return success_response(message.id)



def edit(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    id = get_param_or_fail(request, 'id')
    title = get_param_or_fail(request, 'title')
    text = get_param_or_fail(request, 'text')
    type = get_param_or_fail(request, 'type')

    try:
        category = Message.objects.get(id=id)

        category.title = title
        category.text = text
        category.type = type

        category.save()
    except Message.DoesNotExist:
        return failure_response("Category with this id is not exists")

    return success_response(category.id)


def delete(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    id = get_param_or_fail(request, 'id')

    try:
        quest = Message.objects.get(id=id)
        quest.delete()

        return success_response('1')
    except Message.DoesNotExist:
        return failure_response('Quest is not found')