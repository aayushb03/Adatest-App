import csv
import json

from ..models import *
from .views import *


@api_view(['POST'])
def add_topic(request, session_id):
    """
    Adds a new topic to the database
    :param request: topic and tests: {topic: str, tests: [{test: str, ground_truth: str}]}
    :return: All tests for the provided topic
    """

    data = json.loads(request.body.decode("utf-8"))

    new_topic = data['topic']
    new_prompt_topic = data['prompt_topic']
    tests = data['tests']

    # set header for csv file
    new_data = [['', 'topic', 'input', 'output', 'label', 'labeler', 'description', 'author', 'model score']]
    # add tests for csv file
    for test in tests:
        new_data.append(
            [generate_random_id(), '', test['test'], test['ground_truth'], 'pass', 'adatest_default', '', '', '']
        )

    directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Tests'))
    file_path = os.path.join(directory, f'NTX_{new_topic}_{session_id}.csv')

    # write to csv file
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(new_data)  # Writing all rows including the header

    grader_prompts[session_id][new_topic] = new_prompt_topic

    if MODEL_TYPE == "mistral":
        grader_pipelines[session_id][new_topic] = GeneralGraderPipeline(llama_model, llama_tokenizer, task=new_prompt_topic)
    else:
        grader_pipelines[session_id][new_topic] = cu0_pipeline

    obj_map[session_id][new_topic] = create_obj(model=gen_pipeline[session_id], essayPipeline=grader_pipelines[new_topic], type=f'{new_topic}_{session_id}')
    df_map[session_id][new_topic] = obj_map[session_id][new_topic].df

    for i, row in df_map[session_id][new_topic].head(11).iterrows():
        if row['input'] == '':
            continue

        label = check_lab(new_topic, row['input'], session_id)
        validity = 'approved' if label == row['output'] else 'denied'
        obj = Test(id=i, title=row['input'], validity=validity, topic=new_topic, label=label,
                   ground_truth=row['output'], session_id=session_id)
        obj.save()

    return Response("Topic added successfully!")


@api_view(['DELETE'])
def delete_topic(request, session_id):
    """
    Deletes a topic from the database
    :param request: topic: str
    :return: All topics in the database
    """
    data = json.loads(request.body.decode("utf-8"))
    top = data['topic']

    # delete all tests for the topic
    Perturbation.objects.filter(topic=top, session_id=session_id).delete()
    Test.objects.filter(topic=top, session_id=session_id).delete()
    del grader_pipelines[session_id][top]
    del obj_map[session_id][top]
    del df_map[session_id][top]

    return Response("Topic deleted successfully!")


@api_view(['GET'])
def get_topics(request, session_id):
    """
    Gets all topics from the db
    :return: All topic names
    """
    return Response(grader_pipelines[session_id].keys())

@api_view(['GET'])
def get_topic_prompt(request, topic, session_id):
    """
    Gets the prompt for a topic
    :param request: topic: str
    :return: The prompt for the topic
    """
    return Response(grader_prompts[session_id][topic])


@api_view(['POST'])
def test_topic_prompt(request):
    """
    Tests a topic prompt
    :param request: topic: str, prompt: str
    :return: The model's score for the prompt
    """
    data = json.loads(request.body.decode("utf-8"))

    prompt = data['prompt']
    test = data['test']

    test_pipeline = GeneralGraderPipeline(llama_model, llama_tokenizer, task=prompt) if MODEL_TYPE == "mistral" else cu0_pipeline
    response = test_pipeline(test)

    return Response(response)
