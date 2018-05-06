# -*- coding: UTF-8 -*-

from datetime import datetime, time
from django.db.models import Sum
from django.db import IntegrityError
from api.models import Quest, QuestCategory, UserQuest, Attempt, Config, Team
from api.helpers import *
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from random import choice
from string import ascii_uppercase

from zipfile import *

import os
import json
import chardet
import requests

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
        return failure_response(str(e.args[0]) + e.args[1])


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

        if now < start_game_time.as_datetime() and not request.client.is_admin():
            return failure_response("Game is not started")

        end_game_time = Config.objects.get(key='end')

        game_is_ended = now > end_game_time.as_datetime()
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

        if now < start_game_time.as_datetime():
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
    game_is_ended = now > end_game_time.as_datetime()

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


def set_error(error_text):
    return {
        'error': True,
        'message': error_text
    }


def upload_action(request):
    print(request)
    if request.method != 'POST':
        return failure_response("Allowed only POST parameters")

    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    file = request.FILES['archive']

    tmp_file_name = ''.join(choice(ascii_uppercase) for i in range(12))
    tmp_file_path = '/tmp/' + tmp_file_name

    with open(tmp_file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    if not is_zipfile(tmp_file_path):
        os.remove(tmp_file_path)
        return failure_response("Allowed only zip archives")

    zip = ZipFile(tmp_file_path, 'r')

    path = '/tmp/folder/'
    zip.extractall(path)

    status = {
        'tasks': {},
        'categories': {}
    }

    categories = QuestCategory.objects.all()
    cats = {}
    for c in categories:
        cats[c.name.lower()] = c.id

    for task in os.listdir(path):
        status['tasks'][task] = {
            'error': False,
            'message': ''
        }

        s_task = status['tasks'][task]

        if os.path.isfile(path + task):
            s_task = set_error('%s must be a folder' % task)
            continue

        PATH = path + task + '/main.json'
        if not os.path.isfile(PATH):
            s_task = set_error('Not found main.json file')
            continue

        print("Processing %s" % task)

        file = open(PATH, 'r', encoding='cp437')
        json_file = file.read()

        l = json.loads(json_file)

        try:
            validate(l, json_quest_schema())
        except ValidationError as e:
            return failure_response(e.message)


        if l['category'] and l['category'].lower() not in cats:
            category_name = l['category'].lower()
            category = QuestCategory(name=category_name)
            category.save()

            status['categories'][category_name]
            cats[category_name] = category.id
        else:
            status['categories'][l['category']] = {}

        if type(l['description']) == str:
            full_text = l['description']
        else:
            full_text = l['description']['RU']

        if 'links' in l and type(l['links']) == list and len(l['links']) > 0:
            description = l['description']['RU'] if 'RU' in l['description'] else l['description']
            full_text = description + '</br> <a href="' + l['links'][0].popitem()[1] + '">Вложение</a>'

        file.close()

        print(type(full_text))
        full_text = full_text.encode('utf-8')
        print(full_text)

        file = open(path + task + '/solve.md', 'r', encoding='utf-8')
        solution = file.read()
        payload = {
            'id': 0,
            'title': l['name'].encode('utf-8'),
            'section': cats[l['category'].lower()],
            'score': l['value'],
            'answer': l['flag_key'].encode('utf-8'),
            'author': l['author']['nick'].encode('utf-8') if 'nick' in l['author'] else 'undefined',
            'short_text': full_text,
            'full_text': full_text,
            'tags': l['category'].encode('utf-8'),
            'solution': solution.encode('utf-8'),
            'access_token': request.GET.get('access_token', None)
        }

        print(payload)
        r = requests.post('http://localhost/api/method/quest.create', data=payload)

        print(r.text)

        file.close()

    # archive = request.FILES['archive']

    os.remove(tmp_file_path)

    return success_response('1')
