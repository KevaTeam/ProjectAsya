from api.helpers import success_response
from api.models import QuestCategory
from api.helpers import *

def list(request):
    categories = QuestCategory.objects.values()

    return success_response({
        'items': [entry for entry in categories]
    })


def add(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    name = get_param_or_fail(request, 'name')

    try:
        category = QuestCategory(name=name)

        category.save()
    except Exception as e:
        print(e)
        return failure_response(e.args[0])

    return success_response(category.id)



def edit(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    id = get_param_or_fail(request, 'id')
    name = get_param_or_fail(request, 'name')

    try:
        category = QuestCategory.objects.get(id=id)

        category.name = name
        category.save()
    except QuestCategory.DoesNotExist:
        return failure_response("Category with this id is not exists")

    return success_response(category.id)


def delete(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    id = get_param_or_fail(request, 'id')

    try:
        quest = QuestCategory.objects.get(id=id)
        quest.delete()

        return success_response('1')
    except QuestCategory.DoesNotExist:
        return failure_response('Quest is not found')