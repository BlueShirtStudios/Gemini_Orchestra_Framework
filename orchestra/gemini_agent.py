from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError
import json
from datetime import datetime

from orchestra.agent_configurations import Configurations

class Gemini_Agent():
    def __init__(self, agent_configs: Configurations):
        self._configurations = agent_configs
        self._client = genai.Client()
        self._selected_model = self._get_available_model()
        self._session = None
        self._is_active = False
        self._google_config = None
        
        self._sent_content = None 
        self._token_count = 0
        self._response = None

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
    def is_active(self) -> bool:
        return self._is_active

    @is_active.setter
    def is_active(self, state: bool):
        self._is_active = state

    @property
    def google_config(self):
        return self._google_config

    @property
    def sent_content(self):
        return self._sent_content

    @sent_content.setter
    def sent_content(self, value):
        self._sent_content = value

    @property
    def token_count(self) -> int:
        return self._token_count

    @token_count.setter
    def token_count(self, value: int):
        self._token_count = value

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value: types.GenerateContentResponse):
        self._response = value

    def _encountered_error(self, function_name: str, error_msg: str) -> str:
        return f"Error in {function_name} : {error_msg}"
    
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
                    self.is_active = True
                    return model_name
        
        print(f"ERROR: No suitable model found.")
        return None    
    
    def _refresh_google_config_object(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=self.configurations.system_instructions,
            max_output_tokens=self.configurations.max_output_tokens,
            temperature=self.configurations.temperature,
            top_p=self.configurations.top_p,
            top_k=self.configurations.top_k
        )

    def _create_session(self):
        if not self.google_config:
            self._google_config = self._refresh_google_config_object()
        
        self.session = self.client.chats.create(
            model=self.selected_model,
            config=self.google_config
        )
    
    def agent_status_msg(self) -> str:
        status = "online" if self.is_active else "offline"
        return f"Agent: {self.configurations.agent_name} is {status}."
    
    def determine_content_tokens(self):
        response = self.client.models.count_tokens(
            model=self.selected_model,
            contents=self.sent_content
        )
        self.token_count = response.total_tokens
        
    def read_only_reponse_text(self) -> str:
        return self.response.text
            
    def send_text_message(self):
        #Prepare content
        self.sent_content = self._format_content(self.sent_content)
        
        #Ensure session exists
        if not self.session:
            self._create_session()

        #Check token limits
        self.determine_content_tokens()
        if self.token_count > self.configurations.max_output_tokens:
            return "Query exceeds model max tokens. Aborting request."

        #Get only the question from the formatted content
        question = self.sent_content[0]["parts"][0]["text"]

        #Send question to the agennt
        try:
            response_object = self.session.send_message(question)
            self.response = response_object
        
        except APIError as e:
            return self._encountered_error("send_text_message", f"API error: {e}")
        except (ClientError, ServerError) as e:
            return self._encountered_error("send_text_message", f"Connection error: {e}")