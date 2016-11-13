from django.db.models import Sum
from api.models import Quest, UserQuest, Attempt
from api.helpers import (
    success_response, failure_response,
    get_param_or_fail
)

from datetime import datetime


def list_quest(request):
    quests = Quest.objects.raw('SELECT q.*, (uq."end" > 0) AS "passed" FROM "api_quest" AS q LEFT JOIN "api_userquest" AS uq ON (q.id = uq.quest_id)')

    array = []
    for quest in quests:
        q = quest.to_list()

        if request.client.is_admin():
            q.update({
                'answer': quest.answer
            })

        #TODO: исправить, когда база будет использоваться на полную
        q.update({
            'count': 0,
            'author': request.client.user.name,
            'full_text': q['text']
        })

        array.append(q)

    return success_response({
        'count': len(array),
        'items': array
    })


def take_quest(request):
    try:
        id = get_param_or_fail(request, 'id')

        quest = Quest.objects.get(id=id)
    except Quest.DoesNotExist:
        return failure_response('Quest is not found')
    except Exception as e:
        return failure_response(e.args[0])

    user_quest = UserQuest.objects.filter(
        user=request.client.user,
        quest=quest
    )

    if user_quest:
        return failure_response('You are already take this quest')

    user_quest = UserQuest(user=request.client.user, quest=quest)

    user_quest.save()

    return success_response({})


def pass_answer(request):
    try:
        id = get_param_or_fail(request, 'id')
        answer = get_param_or_fail(request, 'answer')

        quest = Quest.objects.get(id=id)

        user_quest = UserQuest.objects.get(
            user=request.client.user,
            quest=quest
        )
    except Quest.DoesNotExist:
        return failure_response('Quest is not found')
    except UserQuest.DoesNotExist:
        return failure_response('You are not take this quest')
    except Exception as e:
        return failure_response(e.args[0])

    if user_quest.end:
        return success_response(answer.lower() == quest.answer.lower())

    try:
        attempt = Attempt(
            user=request.client.user,
            quest=quest,
            user_answer=answer,
            quest_answer=quest.answer
        )

        attempt.save()

    except Exception as e:
        return failure_response(e.args[0])

    decision = answer.lower() == quest.answer.lower()

    if decision:
        user_quest.end = datetime.now()

        user_quest.save()

        # Пересчитываем рейтинг пользователя (решение проблемы rase-condition)
        rating = UserQuest.objects\
            .filter(user=request.client.user)\
            .exclude(end__isnull=True)\
            .aggregate(total_rating=Sum('quest__score'))

        rating = rating['total_rating'] or 0

        request.client.user.rating = rating
        request.client.user.save()

    return success_response(decision)


