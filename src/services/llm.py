import json
import logging
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from groq import Groq
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from src.config.settings import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class LLMServiceError(Exception):
    pass

class GroqLLMService:
    def __init__(self):
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set.")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate_text(self, prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.0,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            raise LLMServiceError(f"Groq API call failed: {e}")

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str = "You are a helpful assistant.") -> T:
        try:
            # Using JSON mode format instruction
            sys_msg = system_prompt + f"\n\nIMPORTANT: Return ONLY valid JSON matching this schema: {schema.model_json_schema()}"
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            parsed = json.loads(content)
            return schema(**parsed)
        except Exception as e:
            logger.error(f"Error generating structured output: {e}")
            raise LLMServiceError(f"Structured Groq call failed: {e}")
