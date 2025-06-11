# llm_clients/openai_client.py
import openai
from llm_clients.base import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, api_key, model="gpt-4", base_url=None):
        openai.api_key = api_key
        if base_url:
            openai.api_base = base_url
        self.model = model

    def chat(self, messages, temperature=0.2, max_tokens=1024, **kwargs):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response
