# llm_clients/anthropic_client.py
import anthropic
from llm_clients.base import LLMClient

class AnthropicClient(LLMClient):
    def __init__(self, api_key, model="claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def chat(self, messages, temperature=0.2, max_tokens=1024, **kwargs):
        # Convert OpenAI-style messages to Anthropic format
        user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": user_msg}],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response
