import os
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


class LLMClient:
    """thin layer over the model provider
       To make it easy for the system
       to switch between service providers for models
    """

    def __init__(self,model: str = "llama-3.3-70b-versatile"):
        api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=api_key)
        self.model= model
    
    def complete_json(self,system_prompt: str,user_message: str) -> dict:
        """just ask output to the model in json format"""
        try:    
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Ticket Message:\n{user_message}"}
                ],
                temperature=0.0,
                response_format={"type": "json_object"} 
            )
        except Exeption as e:
            raise RuntimeError(f"LLM request failed: {e}") from e
        raw = response.choices[0].message.content
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"model returned invalid JSON: {raw[:200]}") from e