from datetime import datetime, time
from django.db.models import Sum
from django.db import IntegrityError
from api.models import Quest, QuestCategory, UserQuest, Attempt, Config, Team
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
        author = get_param_or_fail(request, 'author')
        short_text = get_param_or_fail(request, 'short_text')
        full_text = get_param_or_fail(request, 'full_text')
        solution = get_param_or_fail(request, 'solution')
        answer = get_param_or_fail(request, 'answer')
        score = get_param_or_fail(request, 'score')

        tags = get_param_or_fail(request, 'tags', False)

        if not category.isdigit():
            return failure_response('Parameter section is incorrect')

        if not score.isdigit():
            return failure_response('Parameter score is incorrect')

        quest_category = QuestCategory.objects.get(id=category)

        params = {
            'name': name,
            'category': quest_category,
            'author': author,
            'short_text': short_text,
            'full_text': full_text,
            'solution': solution,
            'answer': answer,
            'score': score,
            'tags': tags
        }

        if not quest:
            quest = Quest(**params)
        else:
            quest.name = name
            quest.category = quest_category
            quest.author = author
            quest.short_text = short_text
            quest.full_text = full_text
            quest.solution = solution
            quest.answer = answer
            quest.score = score
            quest.tags = tags

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
    if not request.client.log_in:
        return not_logged_response()

    try:
        now = datetime.now()
        start_game_time = Config.objects.get(key='start')

        if now < start_game_time[0].as_datetime():
            return failure_response("Game is not started")

        end_game_time = Config.objects.get(key='end')

        game_is_ended = now > end_game_time[0].as_datetime()
    except Config.DoesNotExist:
        game_is_ended = False
        end_game_time = False

    quests = Quest.objects.raw('''
        SELECT
            q.*,
            COUNT(uq1.id) > 0 AS passed,
            COUNT(uq2.id) AS `count`
        FROM api_quest AS q
            LEFT JOIN api_userquest AS uq1 ON (
                q.id = uq1.quest_id AND
                uq1.user_id IN (SELECT id FROM api_user WHERE team_id = %s) AND
                uq1.end > 0
            )
            LEFT JOIN api_userquest AS uq2 ON (
                q.id = uq2.quest_id AND
                uq2.end IS NOT NULL
            )
        GROUP BY q.id''', [int(request.client.user.team_id)])

    array = []
    for quest in quests:
        q = quest.to_list()

        if request.client.is_admin():
            q.update({
                'answer': quest.answer,
                'solution': quest.solution
            })

        if game_is_ended:
            q.update({
                'solution': quest.solution
            })

        q.update({
            'count': quest.count,
            'author': q['author'],
            'short_text': q['short_text']
        })

        array.append(q)

    return success_response({
        'count': len(array),
        'items': array
    })


def take_quest(request):
    if not request.client.log_in:
        return not_logged_response()

    try:
        now = datetime.now()
        start_game_time = Config.objects.get(key='start')

        if now < start_game_time[0].as_datetime():
            return failure_response("Game is not started")

        id = get_param_or_fail(request, 'id')

        quest = Quest.objects.get(id=id)
    except Config.DoesNotExist:
        return failure_response('Start game is not defined')
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
    if not request.client.log_in:
        return not_logged_response()

    try:
        id = get_param_or_fail(request, 'id')
        answer = get_param_or_fail(request, 'answer')

        quest = Quest.objects.get(id=id)

        user_quest = UserQuest.objects.get(
            user=request.client.user,
            quest=quest
        )

        end_game_time = Config.objects.get(key='end')
    except Quest.DoesNotExist:
        return failure_response('Quest is not found')
    except UserQuest.DoesNotExist:
        return failure_response('You are not take this quest')
    except Config.DoesNotExist:
        return failure_response('End time is not defined')
    except Exception as e:
        return failure_response(e.args[0])

    if user_quest.end:
        return success_response(answer.lower() == quest.answer.lower())

    now = datetime.now()
    game_is_ended = now > end_game_time[0].as_datetime()

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

    if decision and not game_is_ended:
        user_quest.end = datetime.now()

        user_quest.save()

        # Пересчитываем рейтинг пользователя (решение проблемы rase-condition)
        rating = UserQuest.objects\
            .filter(user=request.client.user)\
            .exclude(end__isnull=True)\
            .aggregate(total_rating=Sum('quest__score'))

        # Пишем рейтинг пользователю
        request.client.user.rating = rating['total_rating'] or 0
        request.client.user.save()

        rating = Team.objects.raw('''
           SELECT
              MAX(R.quest) AS id,
              SUM(R.score) AS score
           FROM (SELECT
               UQ.quest_id AS quest,
               Q.score AS score
           FROM api_userquest AS UQ
           INNER JOIN api_quest AS Q ON UQ.quest_id = Q.id
           WHERE
               UQ.user_id IN (SELECT U.id FROM api_user AS U WHERE U.team_id = %s) AND
               UQ.end > 0
           GROUP BY quest_id) AS R;
        ''', [int(request.client.user.team_id)])

        # Обновляем командный рейтинг
        request.client.user.team.score = rating[0].score
        request.client.user.team.save()

    return success_response(decision)


def get_attempts(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    attempts = Attempt.objects.all().order_by('-time')[:100]

    array = []
    for attempt in attempts:
        array.append(attempt.to_list())

    return success_response(array)


def upload_action(request):
    if request.method != 'POST':
        return failure_response("Allowed only POST parameters")

    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    print(request.FILES['archive'])
    # archive = request.FILES['archive']


    return success_response('1')