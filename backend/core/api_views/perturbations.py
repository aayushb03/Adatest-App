import json

from rest_framework import status

from ..models import *
from ..serializer import PerturbationSerializer
from .views import *


@api_view(['POST'])
def generate_perturbations(request, topic, session_id):
    """
    Generates perturbations for the provided topic and stores them in the database
    :param request: list of tests to perturb
    :param topic: current statement topic
    :param session_id: current session id
    :return: All perturbations for the provided topic
    """

    # Load in list of tests
    tests = json.loads(request.body.decode("utf-8"))

    for test in tests:
        # Get test and list of perts for the test
        testData = Test.objects.get(id=test["id"])
        pertList = Perturbation.objects.filter(test_parent=testData, session_id=session_id)

        # Generate default perts for the test
        for perturb_type, pipeline in pert_pipeline_map[session_id].items():
            if pertList.filter(type=perturb_type).exists():
                continue

            if pipeline is not None:
                perturbed_test = pipeline(testData.title)
                perturbed_test = perturbed_test[0]['generated_text']
            else:
                perturbed_test = testData.title

            perturbed_label = check_lab(topic, perturbed_test, session_id)

            if (perturb_type in ["negation", "antonyms"]) ^ (testData.ground_truth == "acceptable"):
                perturbed_gt = "acceptable"
            else:
                perturbed_gt = "unacceptable"

            if (perturb_type in ["negation", "antonyms"]) ^ (testData.ground_truth == perturbed_label):
                perturbed_validity = "approved"
            else:
                perturbed_validity = "denied"

            if perturbed_test == testData.title:
                perturbed_validity = "unapproved"
                perturbed_gt = "unknown"

            perturbed_id = generate_random_id()

            perturbData = Perturbation(test_parent=testData, label=perturbed_label, id=perturbed_id,
                                       title=perturbed_test, type=perturb_type, validity=perturbed_validity, topic=topic,
                                       ground_truth=perturbed_gt, session_id=session_id)
            perturbData.save()

        # Generate custom perts for the test (if applicable)
        for perturb_type, perturb_options in custom_pert_pipeline_map[session_id].items():
            if pertList.filter(type=perturb_type).exists():
                continue

            if custom_pipeline[session_id] is not None:
                perturbed_test = custom_pipeline[session_id](f'{perturb_options["prompt"]}: {testData.title}')
                perturbed_test = perturbed_test[session_id]['generated_text']
            else:
                perturbed_test = testData.title

            perturbed_label = check_lab(topic, perturbed_test, session_id)

            if (perturb_options["flip_label"]) ^ (testData.ground_truth == "acceptable"):
                perturbed_gt = "acceptable"
            else:
                perturbed_gt = "unacceptable"

            if (perturb_options["flip_label"]) ^ (testData.ground_truth == perturbed_label):
                perturbed_validity = "approved"
            else:
                perturbed_validity = "denied"

            if perturbed_test == testData.title:
                perturbed_validity = "unapproved"
                perturbed_gt = "unknown"

            perturbed_id = generate_random_id()

            perturbData = Perturbation(test_parent=testData, label=perturbed_label, id=perturbed_id,
                                       title=perturbed_test, type=perturb_type, validity=perturbed_validity, topic=topic,
                                       ground_truth=perturbed_gt, session_id=session_id)
            perturbData.save()

    allPerturbs = Perturbation.objects.filter(session_id=session_id)
    serializer = PerturbationSerializer(allPerturbs, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_perturbations(request, session_id):
    """
    Getter for perts
    :param request: None
    :return: All perturbations in the database
    """
    data = Perturbation.objects.filter(session_id=session_id)
    serializer = PerturbationSerializer(data, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def edit_perturbation(request, topic, session_id):
    """
    Edits a perturbation in the database
    :param request: Perturbation to be edited
    :param topic: current topic
    :return: All perturbations for the provided topic
    """

    # Get test from request body
    test = json.loads(request.body.decode('utf-8'))['test']

    # Generate AI label
    new_label = check_lab(topic, test['title'], session_id)

    # Get perturbation from db and update fields
    perturbTest = Perturbation.objects.get(id=test["id"])

    perturbTest.title = test["title"]
    perturbTest.label = new_label
    perturbTest.validity = "unapproved"
    perturbTest.save()

    # Get all tests and return them
    test = Perturbation.objects.filter(session_id=session_id)
    serializer = PerturbationSerializer(test, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def validate_perturbations(request, validation, session_id):
    """
    Validates a list of perturbations and updates their fields accordingly
    :param request: list of perturbations to validate
    :param validation: type of validation to apply
    :param session_id: current session id
    :return: All perturbations in the database
    """

    # Load in pert list
    perts = json.loads(request.body.decode("utf-8"))

    if validation not in ["approved", "denied", "invalid"]:
        return Response("Invalid validation type", status=status.HTTP_400_BAD_REQUEST)

    # Iterate through perts and update fields
    for pert in perts:
        perturbData = Perturbation.objects.get(id=pert["id"])

        if validation == "approved":
            perturbData.ground_truth = perturbData.label
            perturbData.validity = "approved"
        elif validation == "denied":
            perturbData.ground_truth = "acceptable" if perturbData.label == "unacceptable" else "unacceptable"
            perturbData.validity = "denied"
        else:
            perturbData.validity = "invalid"

        perturbData.save()

    # Return all perts
    allPerts = Perturbation.objects.filter(session_id=session_id)
    serializer = PerturbationSerializer(allPerts, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_new_pert(request, session_id):
    """
    Adds a new pert type to the db and generates perturbations for the given tests
    :param request: new pert type to add (tests, prompt, flip_label, name)
    :param topic: current topic
    """

    # Load in new pert type and fields
    new_pert = json.loads(request.body.decode("utf-8"))

    test_list = new_pert['test_list']
    prompt = new_pert['prompt']
    prompt = f'{prompt}. Only reply with the revised text and do not add comments'
    flip_label = new_pert['flip_label']
    pert_name = new_pert['pert_name']

    if pert_name in custom_pert_pipeline_map[session_id].keys() or pert_name in pert_pipeline_map[session_id].keys():
        return Response("Invalid perturbation type", status=status.HTTP_400_BAD_REQUEST)

    if pert_name in default_pert_pipeline_map:
        pipeline = pert_pipeline_map[session_id][pert_name]
    else:
        custom_pert_pipeline_map[session_id][pert_name] = {"name": pert_name, "prompt": prompt, "flip_label": flip_label}
        pipeline = custom_pipeline[session_id]

    for test in test_list:
        id = test["id"]
        testData = Test.objects.get(id=id)

        if pipeline is not None:
            if pert_name in default_pert_pipeline_map:
                perturbed_test = pipeline(testData.title)
            else:
                perturbed_test = custom_pipeline[session_id](f'{prompt}: {testData.title}')
            perturbed_test = perturbed_test[0]['generated_text']
        else:
            perturbed_test = testData.title

        perturbed_label = check_lab(testData.topic, perturbed_test, session_id)

        if flip_label ^ (testData.ground_truth == "acceptable"):
            perturbed_gt = "acceptable"
        else:
            perturbed_gt = "unacceptable"

        if flip_label ^ (testData.ground_truth == perturbed_label):
            perturbed_validity = "approved"
        else:
            perturbed_validity = "denied"

        perturbed_id = generate_random_id()

        perturbData = Perturbation(test_parent=testData, label=perturbed_label, id=perturbed_id,
                                   title=perturbed_test, type=pert_name, validity=perturbed_validity, topic=testData.topic,
                                   ground_truth=perturbed_gt, session_id=session_id)
        perturbData.save()

    data = Perturbation.objects.filter(session_id=session_id)
    serializer = PerturbationSerializer(data, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def test_new_pert(request, session_id):
    """
    Tests a new perturbation type
    :param request: {statement: str, prompt: str, pert_name: str}
    :param topic: current topic
    :return: perturbed test case
    """

    # Load in data
    data = json.loads(request.body.decode("utf-8"))

    test_case = data['test_case']
    prompt = data['prompt']

    if custom_pipeline[session_id] is not None:
        perturbed_test = custom_pipeline[session_id](f'{prompt}: {test_case}')
        perturbed_test = perturbed_test[0]['generated_text']
    else:
        perturbed_test = test_case

    return Response(perturbed_test)


@api_view(['DELETE'])
def delete_perturbation(request, session_id):
    """
    Deletes a perturbation from the database
    :param request: needs json object with pert_name in body
    :return: All perturbations in the database
    """

    pert = json.loads(request.body.decode("utf-8"))
    pert_name = pert['pert_name']

    # Get perturbation and delete it
    if pert_name in pert_pipeline_map[session_id]:
        del pert_pipeline_map[session_id][pert_name]
        Perturbation.objects.filter(type=pert_name, session_id=session_id).delete()

    if pert_name in custom_pert_pipeline_map[session_id]:
        del custom_pert_pipeline_map[session_id][pert_name]
        Perturbation.objects.filter(type=pert_name, session_id=session_id).delete()

    # Return all perts
    allPerts = Perturbation.objects.filter(session_id=session_id)
    serializer = PerturbationSerializer(allPerts, context={'request': request}, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_perturbation_type(request, pert_type, session_id):
    """
    Getter for perturbation types
    :param request: None
    :param pert_type: type of perturbation to get
    :param session_id: current session id
    :return: The info of the perturbation type
    """
    if pert_type in custom_pert_pipeline_map[session_id]:
        custom_pert_pipeline_map[session_id][pert_type]["prompt"] = custom_pert_pipeline_map[session_id][pert_type]["prompt"].replace(". Only reply with the revised text and do not add comments", "")
        return Response(custom_pert_pipeline_map[session_id][pert_type])
    elif pert_type in pert_pipeline_map[session_id]:
        return Response({"name": pert_type, "prompt": "Default", "flip_label": pert_type == "negation" or pert_type == "antonyms"})
    else:
        return Response("Invalid perturbation type", status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_perturbation_types(request, session_id):
    """
    Getter for perturbation types
    :param request: None
    :param pert_type: type of perturbation to get
    :return: The info of the perturbation type
    """
    pert_types = list(pert_pipeline_map[session_id].keys()) + list(custom_pert_pipeline_map[session_id].keys())
    return Response(pert_types)


@api_view(['GET'])
def get_default_perturbations(request, config):
    """
    Getter for default perturbations
    :return: The default perturbation types
    """
    if config not in default_pert_pipeline_map:
        return Response("Invalid app config", status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(default_pert_pipeline_map[config])
