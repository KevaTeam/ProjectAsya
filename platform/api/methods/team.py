from api.helpers import success_response
from api.models import Team
from api.helpers import *
import string, random


def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def add_action(request):
    if not request.client.is_admin():
        return failure_response("You don't have sufficient permissions")

    name = get_param_or_fail(request, 'name')
    score = 0
    token = randomword(10)

    try:
        team = Team(name=name, score=score, token=token)

        team.save()
    except Exception as e:
        print(e)
        return failure_response(e.args[0])

    return success_response(team.id)
