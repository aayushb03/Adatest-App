from django.urls import include, path

from .api_views import logs, perturbations, tests, topics, views
from .api_views.views import index

urlpatterns = [
    path('', index, name='index'),
    path('', include("django_nextjs.urls")),

    path('core/session/get/<str:session_id>', views.get_app_config),
    path('core/session/check/<str:session_id>', views.check_session),

    # Test endpoints (api_views/tests.py)
    path('core/tests/get/<str:topic>/<str:session_id>', tests.get_by_topic),
    path('core/tests/post/<str:topic>/<str:session_id>', tests.test_generate),
    path('core/tests/clear/<str:config>/<str:session_id>', tests.test_clear),
    path('core/tests/delete/<str:pk>', tests.test_delete),
    path('core/tests/init/<str:session_id>', views.init_database),
    path('core/tests/all/<str:session_id>', tests.get_all_tests),
    path('core/tests/add/<str:topic>/<str:ground_truth>/<str:session_id>', tests.add_test),
    path('core/tests/edit/<str:topic>/<str:session_id>', tests.edit_test),
    path('core/tests/process/<str:decision>/<str:topic>/<str:session_id>', tests.process_list),

    # Log endpoints (api_views/logs.py)
    path('core/logs/add/<str:session_id>', logs.log_action),
    path('core/logs/clear/<str:session_id>', logs.log_clear),
    path('core/logs/save/<str:session_id>', logs.save_log),

    # Perturbation endpoints (api_views/perturbations.py)
    path('core/perturbations/generate/<str:topic>/<str:session_id>', perturbations.generate_perturbations),
    path('core/perturbations/get/<str:session_id>', perturbations.get_perturbations),
    path('core/perturbations/validate/<str:validation>/<str:session_id>', perturbations.validate_perturbations),
    path('core/perturbations/edit/<str:topic>/<str:session_id>', perturbations.edit_perturbation),
    path('core/perturbations/add/<str:session_id>', perturbations.add_new_pert),
    path('core/perturbations/test/<str:session_id>', perturbations.test_new_pert),
    path('core/perturbations/delete/<str:session_id>', perturbations.delete_perturbation),
    path('core/perturbations/getType/<str:pert_type>/<str:session_id>', perturbations.get_perturbation_type),
    path('core/perturbations/getAll/<str:session_id>', perturbations.get_all_perturbation_types),
    path('core/perturbations/getDefault/<str:config>', perturbations.get_default_perturbations),

    # Topic endpoints (api_views/topics.py)
    path('core/topics/add/<str:session_id>', topics.add_topic),
    path('core/topics/get/<str:session_id>', topics.get_topics),
    path('core/topics/prompt/<str:topic>/<str:session_id>', topics.get_topic_prompt),
    path('core/topics/delete/<str:session_id>', topics.delete_topic),
    path('core/topics/test', topics.test_topic_prompt)
]




