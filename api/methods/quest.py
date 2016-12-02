from datetime import datetime
from django.db.models import Sum
from django.db import IntegrityError
from api.models import Quest, QuestCategory, UserQuest, Attempt
from api.helpers import *


def create_quest(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    return handle_quest(request, quest=None)


def edit_quest(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    id = get_param_or_fail(request, 'id')
    try:
        quest = Quest.objects.get(id=id)
    except Quest.DoesNotExist:
        return handle_quest(request, quest=None)

    return handle_quest(request, quest=quest)


def handle_quest(request, quest):
    try:
        name = get_param_or_fail(request, 'title')
        category = get_param_or_fail(request, 'section')
        text = get_param_or_fail(request, 'full_text')
        answer = get_param_or_fail(request, 'answer')
        score = get_param_or_fail(request, 'score')

        if not category.isdigit():
            return failure_response('Parameter section is incorrect')

        if not score.isdigit():
            return failure_response('Parameter score is incorrect')

        quest_category = QuestCategory.objects.get(id=category)

        if not quest:
            quest = Quest(
                name=name,
                category=quest_category,
                text=text,
                answer=answer,
                score=score
            )
        else:
            quest.name = name
            quest.category = quest_category
            quest.text = text
            quest.answer = answer
            quest.score = score

        quest.save()

        return success_response(quest.id)

    except QuestCategory.DoesNotExist:
        return failure_response('Quest category does not exists')
    except IntegrityError:
        return failure_response('Quest with the same name is already exists')
    except Exception as e:
        print(e)
        return failure_response(e.args[0])


def delete_quest(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    id = get_param_or_fail(request, 'id')

    try:
        quest = Quest.objects.get(id=id)
        quest.delete()

        return success_response('1')
    except Quest.DoesNotExist:
        return failure_response('Quest is not found')


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
            'author': 'noname',
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


def get_attempts(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    attempts = Attempt.objects.all().order_by('time')

    array = []
    for attempt in attempts:
        array.append(attempt.to_list())

    return success_response(array)