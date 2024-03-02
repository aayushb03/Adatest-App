from adatest import _prompt_builder
from adatest import TestTree
from adatest import * 
import os 

from adatest import generators
import pandas as pd


from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import Pipeline




def load_model(model_name):
    model = T5ForConditionalGeneration.from_pretrained(model_name)
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model.eval()
    return model, tokenizer

class CustomEssayPipeline(Pipeline):
        @staticmethod
        def load_model(model_name):
            model = T5ForConditionalGeneration.from_pretrained(model_name)
            tokenizer = T5Tokenizer.from_pretrained(model_name)
            model.eval()
            return model, tokenizer

        def __init__(self, model, tokenizer, task="essay-classification"):
            super().__init__(model, tokenizer, task)

        def preprocess(self, essay):
            prompt = f"According to the following essay, classify the student's definition of LCE as {{option_1: Acceptable}}, {{option_2: Unacceptable}}\n{essay}"
            inputs = self.tokenizer(prompt, return_tensors="pt", padding="max_length", truncation=True, max_length=512)
            return inputs

        def _forward(self, inputs, **kwargs):
            outputs = self.model.generate(inputs['input_ids'], attention_mask=inputs['attention_mask'], max_new_tokens=50)
            return outputs

        def postprocess(self, model_outputs):
            prediction = self.tokenizer.decode(model_outputs[0], skip_special_tokens=True)
            return prediction

        def __call__(self, essay):
            if isinstance(essay, str):   
                inputs = self.preprocess(essay)
                outputs = self._forward(inputs)
                temp = []
                temp.append(self.postprocess(outputs))
                return temp
            else: 
                temp = []
                for ess in essay: 
                    inputs = self.preprocess(ess)
                    outputs = self._forward(inputs)
                    temp.append(self.postprocess(outputs))
                return temp

        def _sanitize_parameters(self, **kwargs):
            # Validate and set default values for parameters
            valid_tasks = ["essay-classification", "other-task"]
            if "task" in kwargs:
                if kwargs["task"] not in valid_tasks:
                    raise ValueError(f"Invalid task. Supported tasks are: {valid_tasks}")
            else:
                kwargs["task"] = "essay-classification"
                

            # Add more parameter validation and default values if needed
            valid_models = ["aanandan/FlanT5_AdaTest_LCE_v2", "aanandan/FlanT5_AdaTest_PE_v2", "aanandan/FlanT5_AdaTest_KE_v2"]
            if "model" in kwargs:
                if kwargs["model"] not in valid_models:
                    raise ValueError(f"Invalid model. Supported models are: {valid_models}")
            else:
                    kwargs["model"], kwargs["tokenizer"] = self.model, self.tokenizer
                

            return kwargs




class AdaClass(): 
    def __init__(self, browser):
        self.browser = browser
        self.df = browser.test_tree._tests
    def generate(self):
        self.browser.generate_suggestions()  
        self.df = self.browser.test_tree._tests
    def check_col(self):
        list = []
        for row in self.df.iterrows():
            if row['topic'].contains('suggestions'): 
                list.append("Unknown")
            else: 
                list.append("Inputed Test")
        self.df["validity"] = list

    def compute_statistics(self): 
        count = 0
        for row in self.df.iterrows(): 
            if row['topic'].contains('suggestions'): 
                if row["Validity"] == "Approved": 
                    count+=1 
        return count 

    def approve(self, test): 
        self.df.loc[self.df['Input'] == test]["Validity"] = "Approved"




def create_obj(): 

    csv_filename = os.path.join(os.path.dirname(__file__), 'NTX_Test.csv')
    test_tree = TestTree(pd.read_csv(csv_filename, index_col=0, dtype=str, keep_default_na=False))

    lce_model, lce_tokenizer = load_model('aanandan/FlanT5_AdaTest_LCE_v2')
    lce_pipeline = CustomEssayPipeline(model=lce_model, tokenizer=lce_tokenizer)

    OPENAI_API_KEY = "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"
    generator = generators.OpenAI('davinci-002', api_key=OPENAI_API_KEY)
    browser = test_tree.adapt(lce_pipeline, generator)
    df1 = browser.test_tree._tests
    obj = AdaClass(browser)

    return obj

obj = create_obj()
print(obj.df)
