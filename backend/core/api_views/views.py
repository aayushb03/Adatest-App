from django_nextjs.render import render_nextjs_page_sync
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..ada import *
from ..models import *
# from ..pipelines.flanT5Grader import *
from ..pipelines.robertaGrader import *
from ..pipelines.llama3Grader import *
from ..pipelines.llama3Generator import *
from ..pipelines.mistralGenerator import *

load_dotenv()
# Check if MODEL is in .env file
if "MODEL" not in os.environ:
    raise ValueError("the env file is wrong")

MODEL_TYPE = os.getenv('MODEL')

# helper objects
# lce_model, lce_tokenizer = load_flant5_model('aanandan/FlanT5_AdaTest_LCE_v2')
# lce_pipeline = CustomEssayPipeline(model=lce_model, tokenizer=lce_tokenizer)
#
# pe_model, pe_tokenizer = load_flant5_model('aanandan/FlanT5_AdaTest_PE_v2')
# pe_pipeline = CustomEssayPipeline(model=pe_model, tokenizer=pe_tokenizer)
#
# ke_model, ke_tokenizer = load_flant5_model('aanandan/FlanT5_AdaTest_KE_v2')
# ke_pipeline = CustomEssayPipeline(model=ke_model, tokenizer=ke_tokenizer)

cu0_pipeline = CUPipeline("CU0")
cu5_pipeline = CUPipeline("CU5")

# pipelines for graders and prompts (access with grades_pipelines[session_id][topic])
grader_pipelines = {}
grader_prompts = {}


# HELPER FUNCTIONS
def generate_random_id():
    random_uuid = uuid.uuid4()
    random_id = random_uuid.hex
    return random_id


def check_lab(type, inp, session_id):
    """
    Checks AI Grade for test
    :param type: type/topic of pipeline
    :param inp: test input
    :param session_id: session id
    :return: acceptable/unacceptable
    """
    if type not in grader_pipelines[session_id].keys():
        return 'unacceptable'

    lab = grader_pipelines[session_id][type](inp)
    return lab[0].lower() if lab[0].lower() in ['acceptable', 'unacceptable'] else 'unacceptable'


def index(request):
    return render_nextjs_page_sync(request)


# mode: AIBAT, MINI-AIBAT, M-AIBAT
appConfig = {}

gen_pipeline = {}
custom_pipeline = {}
pert_pipeline_map = {
    # will fill up with perturbations
}
custom_pert_pipeline_map = {
    # will fill up with custom perturbations
}
default_pert_pipeline_map = {
    "AIBAT": ['spelling', 'negation', 'synonyms', 'paraphrase', 'acronyms', 'antonyms', 'spanish'],
    "Mini-AIBAT": ['spelling', 'synonyms', 'paraphrase', 'acronyms', 'spanish'],
    "M-AIBAT": ['spanish', 'spanglish', 'english', 'nouns', 'spelling', 'cognates', 'dialect', 'loan_word']
}

## TODO: separate model initializations on config instead of all pipelines 
if MODEL_TYPE == "mistral":
    print("Loading Llama Model")
    # Load llama model for generation and grader
    llama_model, llama_tokenizer = load_llama3_model('meta-llama/Meta-Llama-3-8B-Instruct')
    llama_gen_pipeline = LlamaGeneratorPipeline(llama_model, llama_tokenizer, task="base")
    llama_custom_pipeline = LlamaGeneratorPipeline(llama_model, llama_tokenizer, task="custom")

    print("Loading Mistral Model")
    # Load mistral model for generation
    mistral_model, mistral_tokenizer = load_mistral_model()
    mistral_gen_pipeline = MistralPipeline(mistral_model, mistral_tokenizer, task="base")
    mistral_custom_pipeline = MistralPipeline(mistral_model, mistral_tokenizer, task="custom")

obj_map = {}
df_map = {}


# create default vals in db
@api_view(['POST'])
def init_database(request, session_id):
    for top, pipe in grader_pipelines[session_id].items():
        obj_map[session_id][top] = create_obj(model=gen_pipeline[session_id], essayPipeline=pipe,
                                              type=f"{top}_esp" if (appConfig[session_id] == "M-AIBAT" and "CU" in top) else top)
        df_map[session_id][top] = obj_map[session_id][top].df
        # PE KE LCE for this user study will have no tests
        data = obj_map[session_id][top].df
        for i, row in data.iterrows():
            if row['input'] == '':
                continue
            obj = Test(id=i, title=row['input'], topic=top, label=check_lab(top, row['input'], session_id), session_id=session_id)
            obj.save()

    return Response("All initial tests loaded!")


@api_view(['GET'])
def get_app_config(request, session_id):
    return Response(appConfig[session_id])


@api_view(['GET'])
def check_session(request, session_id):
    return Response(session_id in appConfig, status=200)
