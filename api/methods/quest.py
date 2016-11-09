from api.models import Quest
from api.helpers import success_response

def list(request):
    quests = Quest.objects.all()

    return success_response({})