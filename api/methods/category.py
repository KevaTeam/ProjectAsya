from api.helpers import success_response
from api.models import QuestCategory

def list(response):
    categories = QuestCategory.objects.values()

    return success_response({
        'items': [entry for entry in categories]
    })