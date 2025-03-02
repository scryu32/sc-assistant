from openai import OpenAI
import os
from .logger import log_decorator
from .vectors import VectorStore

class AssistantModel:
    #user_information 데이터구조:
    #{username:이름, user_uuid: uuid, email:email, age, ...}
    def __init__(self, user_information, openai_api=os.environ.get('OPENAI_KEY'), log=False):
        self.log = log
        self.user_information= user_information
        self.client = OpenAI(api_key=openai_api)
    
    #로깅
    def __getattribute__(self, name):
        log_enabled = object.__getattribute__(self, "log")
        attr = object.__getattribute__(self, name)
        if not log_enabled or not callable(attr) or name.startswith("__"):
            return attr
        if hasattr(attr, "__wrapped__"):
            return attr
        decorated = log_decorator(attr)
        object.__setattr__(self, name, decorated)
        return decorated
    
    #stream으로 텍스트 반환
    def stream_chat(self, messages: list):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1600,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stream=True
        )
        
        for chunk in response:
            if chunk and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield content
    