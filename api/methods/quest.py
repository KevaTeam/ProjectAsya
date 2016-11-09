from api.models import Quest
from api.helpers import (
    success_response, failure_response,
    get_param_or_fail
)

def list(request):
    quests = Quest.objects.all()

    array = []
    for quest in quests:
        q = quest.to_list()

        if request.client.is_admin():
            q.update({
                'answer': quest.answer
            })

        #TODO: исправить, когда база будет использоваться на полную
        q.update({
            'passed': True,
            'count': 0
        })

        array.append(q)

    return success_response({
        'count': len(array),
        'items': array
    })

def take(request):
    try:
        id = get_param_or_fail(request, 'id')
    except Exception as e:
        return failure_response(e.args[0])

