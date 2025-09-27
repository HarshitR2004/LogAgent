import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class LLM:
    """Singleton class to manage the LLM model instance."""
    _models = {}
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_model(self, model_name):
        if model_name not in self._models:
            self._models[model_name] = ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                model=model_name,
                temperature=0.1,
            )
        return self._models[model_name]