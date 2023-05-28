import os
import logging

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp
from langchain import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from config import OPENAI_API_KEY, INDEX, PINECONE_API_KEY, PINECONE_REGION


#from pinecone import Client
# client = Client(api_key=PINECONE_API_KEY, region=PINECONE_REGION)


class ModelInitializer:

    def __init__(self, model_base_path, initialize_models=True):
        self.model_base_path = model_base_path
        self.models = {}
        self.initialize_models = initialize_models

    def add_model(self, model_name, relative_path):
        if not self.initialize_models:
            return
        full_path = os.path.join(self.model_base_path, relative_path)
        if os.path.isfile(full_path):
            self.models[model_name] = LlamaCpp(streaming=True, callbacks=[StreamingStdOutCallbackHandler()], model_path=full_path, n_ctx=2048)
        else:
            logging.warning(f"Model file {relative_path} not found. Model {model_name} not initialized.")

    def get_model(self, model_name):
        return self.models.get(model_name)

INITIALIZE_MODELS = False  # Change this to control the initialization of models
model_base_path = os.getenv('MODEL_PATH')

initializer = ModelInitializer(model_base_path, initialize_models=INITIALIZE_MODELS)
if INITIALIZE_MODELS:
    initializer.add_model('wizard_7b', 'wizard_7b/WizardLM-7B-uncensored.ggmlv3.q4_1.bin')
    initializer.add_model('manticore_13b', 'manticore_13b/Manticore-13B-Chat-Pyg.ggmlv3.q4_0.bin')


embeddings = OpenAIEmbeddings()
memory_llm = ChatOpenAI(temperature=0.1, model_name="gpt-3.5-turbo")
turbo_llm = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")
detail_llm = ChatOpenAI(temperature=1, model_name="gpt-4")


wizard_7b = initializer.get_model('wizard_7b')
manticore_13b = initializer.get_model('manticore_13b')


