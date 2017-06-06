from api.models import *

from api.helpers import *


def list_action(request):
    teams = Team.objects.raw('''
        SELECT
            T.id,
            T.name,
            T.score,
            COALESCE(T2.incorrect_answer, 0) AS count_incorrect
        FROM api_team AS T
        LEFT JOIN
            (SELECT
                U.team_id,
                COUNT(A.quest_id) AS incorrect_answer
            FROM api_user AS U
                LEFT JOIN api_attempt AS A ON (
                    A.user_id = U.id AND
                    A.quest_answer <> A.user_answer
                    )
            GROUP BY U.team_id) AS T2
        ON
            T.id = T2.team_id
        ORDER BY T.score DESC, count_incorrect
        ''')

    array = []
    for team in teams:
        array.append({
            'id': team.id,
            'name': team.name,
            'score': team.score,
            'incorrect': team.count_incorrect
        })

    return success_response({
        'count': len(array),
        'items': array
    })
