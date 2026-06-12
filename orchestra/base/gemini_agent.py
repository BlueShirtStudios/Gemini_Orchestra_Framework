import abc
import json
from typing import Generator
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError

from orchestra.base.agent_configurations import Configurations

class Gemini_Agent():
    def __init__(self, agent_configs: Configurations):
        #Session Details
        self._client = genai.Client()
        self._active = False
        
        #Agent Details
        self._configurations = agent_configs
        self._selected_model = self._get_available_model()
        self._session = None
        self._google_config = None

        #Response and Paylaod tokens
        self._google_response_obj = None
        self._payload_tokens = 0
        self._session_tokens = 0

    @property
    def configurations(self):
        return self._configurations

    @property
    def client(self):
        return self._client

    @property
    def selected_model(self):
        return self._selected_model

    @selected_model.setter
    def selected_model(self, value: str):
        self._selected_model = value

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, state: bool):
        self._active = state

    @property
    def google_config(self) -> types.GenerateContentConfig:
        return self._google_config
    
    @google_config.setter
    def google_config(self, goog_cfg : types.GenerateContentConfig):
        self._google_config = goog_cfg

    @property
    def payload_tokens(self) -> int:
        return self._payload_tokens

    @payload_tokens.setter
    def payload_tokens(self, value: int):
        self._payload_tokens = value

    @property
    def google_response_obj(self):
        return self._google_response_obj

    @google_response_obj.setter
    def google_response_obj(self, value: types.GenerateContentResponse):
        self._google_response_obj = value
        
    @property
    def session_tokens(self) -> int:
        return self._session_tokens
    
    @session_tokens.setter
    def session_tokens(self, val: int):
        self._session_tokens = val

    def _encountered_error(self, function_name: str, error_msg: str) -> str:
        print(f"Error in {function_name} : {error_msg}")
    
    def _format_content(self, content: str):
        clean_content = content.strip()
        formatted_data = [
            {
            "role": "user",
            "parts": [{"text" : clean_content}]
            }
        ]
        return formatted_data
        
    def _get_available_model(self) -> str:
        available_models = [m.name for m in self.client.models.list() if 'generateContent' in m.supported_actions]
        
        for preferred in self.configurations.preferred_models:
            for model_name in available_models:
                if model_name.startswith(f"models/{preferred}") or model_name == preferred:
                    self.active = True
                    return model_name
        
        print(f"ERROR: No suitable model found.")
        return None    
    
    def _refresh_google_config_object(self) -> types.GenerateContentConfig:
        config_kwargs =  {
            "system_instruction": self.configurations.system_instructions,
            "max_output_tokens": self.configurations.max_session_tokens,
            "temperature": self.configurations.temperature,
            "top_p": self.configurations.top_p,
            "top_k": self.configurations.top_k
        }
        
        if self.configurations.response_schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = self.configurations.response_schema
            
        return types.GenerateContentConfig(**config_kwargs)

    def _ensure_session(self):
        if not self.google_config:
            self.google_config = self._refresh_google_config_object()
        
        self.session = self.client.chats.create(
            model=self.selected_model,
            config=self.google_config
        )
    
    def agent_status_msg(self) -> str:
        status = "online" if self.active else "offline"
        return f"Agent: {self.configurations.agent_name} is {status}."
    
    def calculate_tokens(self, payload: str) -> int:
        response = self.client.models.count_tokens(
            model=self.selected_model,
            contents=payload
        )
            
        return response.total_tokens
            
    def send_small_payload(self, payload: str) -> json:
        #Checks if agent is active
        if not self.active or not self.selected_model:
            return "Agent is Offline" 
        
        self._ensure_session()

        #Check token limits
        self.max_payload_tokens = self.calculate_tokens(payload)
        if self.max_payload_tokens > self.configurations.max_payload_tokens:
            self._encountered_error(self.send_small_payload.__name__, "Query exceeds model max tokens. Aborting request.")
        
        self.session_max_tokens = self.calculate_session_tokens()
        if self.session_tokens > self.configurations.max_session_tokens:
            self._encountered_error(self.send_small_payload.__name__, "Session tokens exceed the max allowed tokens. Aborting request.")

        #Send question to the agent
        try:
            response_object = self.session.send_message(payload)
            self.google_response_obj = response_object
            return response_object.text
        
        except APIError as e:
            return self._encountered_error("send_text_message", f"API error: {e}")
        except (ClientError, ServerError) as e:
            return self._encountered_error("send_text_message", f"Connection error: {e}")
            
    def execute_stream_payload(self, payload: str, **kwargs) -> Generator[str, None, None]:
        if not self.active or not self.selected_model:
            yield "Agent is offline or uninitialized."
            return

        self._ensure_session()

        #Check total payload weight ahead of streaming
        self.session_max_tokens = self.calculate_session_tokens()
        if self.session_tokens > self.configurations.max_session_tokens:
            self._encountered_error(self.send_small_payload.__name__, "Session tokens exceed the max allowed tokens. Aborting request.")

        try:
            full_response = ""
            #Native SDK Streaming loop handler
            response_stream = self._session.send_message_stream(payload)
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    
        except (APIError, ClientError, ServerError) as e:
            yield self.format_error("execute_stream", f"Streaming fault: {e}")
            
    def get_session_history(self):
        #Get the history from Genai auto track
        return self.session.get_history()
    
    def calculate_session_tokens(self) -> int:
        if not self.session:
            return 0
    
        current_history = self.get_session_history()
        
        #Determine the current session token count
        if len(current_history) == 0:
            return
        
        response = self.client.models.count_tokens(
            model=self.selected_model,
            contents=current_history
        )
        return response.total_tokens
    
    def get_total_available_tokens(self) -> int:
        return self.configurations.max_session_tokens - self.session_tokens