import json
import sqlite3

from rest_framework import status

from .views import *
from ..ada import *
from ..models import *


@api_view(['POST'])
def log_action(request, session_id):
    byte_string = request.body
    body = byte_string.decode("utf-8")
    body_dict = json.loads(body)
    test_ids = body_dict['data']['test_ids']
    action = body_dict['data']['action']

    log = Log(test_ids=test_ids, action=action, session_id=session_id)
    try:
        log.save()
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response("Log Successfully Added!")


@api_view(['POST'])
def save_log(request, session_id, name):
    save_dir = os.path.join(os.getcwd(), "logs", f'{name}_{str(session_id)}')
    os.makedirs(save_dir, exist_ok=True)

    # Save Log table to CSV
    logs = Log.objects.filter(session_id=session_id).values()
    log_df = pd.DataFrame(list(logs))
    log_df.to_csv(os.path.join(save_dir, 'log.csv'), index=False)

    # Save perturbations table to csv called log.csv
    perturbations = Perturbation.objects.filter(session_id=session_id).values()
    perturbations_df = pd.DataFrame(list(perturbations))
    perturbations_df.to_csv(os.path.join(save_dir, 'perturbations.csv'), index=False)

    # Save tests table to csv called log.csv
    tests = Test.objects.filter(session_id=session_id).values()
    tests_df = pd.DataFrame(list(tests))
    tests_df.to_csv(os.path.join(save_dir, 'tests.csv'), index=False)

    # Delete all logs
    Log.objects.filter(session_id=session_id).delete()

    return Response("Data saved to CSV successfully!")


@api_view(['DELETE'])
def log_clear(request, session_id):
    logs = Log.objects.filter(session_id=session_id)
    for log in logs:
        log.delete()
    return Response("All logs cleared!")
