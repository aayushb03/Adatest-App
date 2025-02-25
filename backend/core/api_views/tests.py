import json
from rest_framework import status
from django.db.models import Q

from ..models import *
from ..serializer import TestSerializer
from .views import *


@api_view(['GET'])
def get_all_tests(request, session_id):
    """
    Gets all tests from the db
    """
    tests = Test.objects.filter(session_id=session_id)
    serializer = TestSerializer(tests, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_by_topic(request, topic, session_id):
    """
    Gets all tests for the provided topic
    :param request: empty body
    :param topic: current topic
    :param session_id: current session id
    """
    suggested = f"suggested_{topic}"
    tests = Test.objects.filter((Q(topic=topic) | Q(topic=suggested)) & Q(session_id=session_id))
    serializer = TestSerializer(tests, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def test_generate(request, topic: str, session_id):
    """
    Generates test cases for the provided topic and stores them in the database
    :param request: empty body
    :param topic: current statement topic
    :param session_id: current session id
    :return: All test cases for the provided topic
    """
    obj = obj_map[session_id][topic]
    obj.generate()
    data = obj.df
    for i, row in data.iterrows():
        if row['topic'].__contains__("suggestions"):
            test = Test(id=i, title=row['input'], topic=f'{topic}', label=check_lab(topic, row['input'], session_id), session_id=session_id)
            test.save()

    suggested = f"suggested_{topic}"
    testData = Test.objects.filter((Q(topic=topic) | Q(topic=suggested)) & Q(session_id=session_id))
    serializer = TestSerializer(testData, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def process_list(request, decision: str, topic: str, session_id):
    """
    Processes a list of tests based on the decision provided and updates the database accordingly
    :param request: list of test cases
    :param decision: approved, denied, or invalid
    :param topic: current statement topic
    :param session_id: current session id
    :return: updated list of test cases
    """

    # Load in tests
    tests = json.loads(request.body.decode("utf-8"))
    df = df_map[session_id][topic]

    # Iterate through tests and update accordingly
    for test in tests:
        test_id = test["id"]

        # Get test from db
        testData = Test.objects.get(id=test_id)

        # Update fields
        testData.validity = decision

        if decision == "approved":
            testData.ground_truth = testData.label
            df_row = df.loc[df['input'] == testData.title]
            df_row["topic"] = ""
        elif decision == "denied":
            if testData.label == "unacceptable":
                testData.ground_truth = "acceptable"
            else:
                testData.ground_truth = "unacceptable"
        elif decision == "invalid":
            testData.title = test["title"]
            indexAge = df[df['input'] == testData.title].index
            df.drop(indexAge, inplace=True)

        testData.save()

    # Get all tests for the topic
    suggested = f"suggested_{topic}"
    allTests = Test.objects.filter((Q(topic=topic) | Q(topic=suggested)) & Q(session_id=session_id))
    serializer = TestSerializer(allTests, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_test(request, topic, ground_truth, session_id):
    """
    Adds a test to the database and returns all tests for the provided topic
    :param request: test case to be added
    :param topic: current topic
    :param ground_truth:
    :param session_id: current session id
    :return: All tests for the provided topic
    """

    # Load in test from body and check AI label
    test = json.loads(request.body.decode("utf-8"))['test']
    gen_label = check_lab(topic, test['title'], session_id)
    if gen_label == ground_truth:
        validity = "approved"
    else:
        validity = "denied"

    # Create test and save to db
    testData = Test(id=generate_random_id(), title=test['title'], topic=topic, validity=validity, label=gen_label,
                    ground_truth=ground_truth, session_id=session_id)
    testData.save()

    # Add to adatest dataframe
    df = df_map[session_id][topic]
    df.loc[len(df)] = {'': testData.id, 'topic': '', 'input': testData.title, 'output': ground_truth, 'label': 'pass',
                       'labeler': 'adatest_default', 'description': '', 'author': '', 'model score': ''}

    # Get all tests for the topic and return them in response
    allTests = Test.objects.filter((Q(topic=topic) | Q(topic=f"suggested_{topic}")) & Q(session_id=session_id))
    serializer = TestSerializer(allTests, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def edit_test(request, topic, session_id):
    """
    Edits a test in the database and returns all tests for the provided topic
    :param request: test case to be edited
    :param topic: current topic
    :return: All tests for the provided topic
    """

    # Load in test and get AI label
    test = json.loads(request.body.decode("utf-8"))['test']
    gen_label = check_lab(topic, test['title'], session_id)

    # Load in test from db and update fields
    testData = Test.objects.get(id=test['id'])

    testData.title = test['title']
    testData.label = gen_label
    testData.validity = "unapproved"
    testData.ground_truth = "unknown"
    testData.save()

    # Get all tests and return them in response
    allTests = Test.objects.filter((Q(topic=topic) | Q(topic=f"suggested_{topic}")) & Q(session_id=session_id))
    serializer = TestSerializer(allTests, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
def test_clear(request, config, session_id):
    """
    Removes all tests from the database
    """

    # delete all tests and perts
    Perturbation.objects.filter(session_id=session_id).delete()
    Test.objects.filter(session_id=session_id).delete()

    if config not in default_pert_pipeline_map:
        return Response("Invalid Configuration", status=status.HTTP_400_BAD_REQUEST)
    perts = default_pert_pipeline_map[config]

    # reset appConfig
    appConfig[session_id] = config
    # reset perturbation pipelines
    pert_pipeline_map[session_id] = {}
    for pert in perts:
        if MODEL_TYPE == "mistral":
            if appConfig[session_id] == "AIBAT" or appConfig[session_id] == "Mini-AIBAT":
                pert_pipeline_map[session_id][pert] = MistralPipeline(mistral_model, mistral_tokenizer, task=pert)
                custom_pipeline[session_id] = mistral_custom_pipeline
                gen_pipeline[session_id] = mistral_gen_pipeline
            if appConfig[session_id] == "M-AIBAT":
                pert_pipeline_map[session_id][pert] = LlamaGeneratorPipeline(llama_model, llama_tokenizer, task=pert)
                custom_pipeline[session_id] = llama_custom_pipeline
                gen_pipeline[session_id] = mistral_gen_pipeline
        else:
            pert_pipeline_map[session_id][pert] = None
            custom_pipeline[session_id] = None
            gen_pipeline[session_id] = None

    grader_pipelines[session_id] = {}
    grader_prompts[session_id] = {}
    obj_map[session_id] = {}
    df_map[session_id] = {}

    # reset grader prompts
    grader_prompts[session_id]['CU0'] = 'Does the following contain the physics concept: Greater height means greater energy? Here is the sentence:'
    grader_prompts[session_id]['CU5'] = 'The sentence is acceptable if it contain the physics concept: The more mass, the more energy. If not, it is unacceptable. Here is the sentence:'
    grader_prompts[session_id]['Food'] = 'Does this sentence include a description of food and/or culture? Here is the sentence:'


    # reset grader pipelines
    if appConfig[session_id] == "M-AIBAT":
        grader_pipelines[session_id]['CU0'] = GeneralGraderPipeline(llama_model, llama_tokenizer, task=grader_prompts[session_id]['CU0']) if MODEL_TYPE == "mistral" else cu0_pipeline
        grader_pipelines[session_id]['CU5'] = GeneralGraderPipeline(llama_model, llama_tokenizer, task=grader_prompts[session_id]['CU5']) if MODEL_TYPE == "mistral" else cu5_pipeline
        grader_pipelines[session_id]['Food'] = GeneralGraderPipeline(llama_model, llama_tokenizer, task=grader_prompts[session_id]['Food']) if MODEL_TYPE == "mistral" else cu0_pipeline
    else:
        grader_pipelines[session_id]['CU0'] = cu0_pipeline
        grader_pipelines[session_id]['CU5'] = cu5_pipeline

    # clear custom perturbations
    custom_pert_pipeline_map[session_id] = {}

    return Response("All tests cleared!")


@api_view(['DELETE'])
def test_delete(request, id: str):
    """
    Deletes a test from the database
    :param request: test id
    """

    test = Test.objects.get(id=id)
    test.delete()

    return Response('Test Successfully Deleted!')
