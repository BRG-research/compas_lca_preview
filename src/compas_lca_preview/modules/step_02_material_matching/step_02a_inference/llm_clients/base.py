# llm_clients/base.py
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    def chat(self, messages: list, temperature=0.2, max_tokens=1024, **kwargs):
        pass
