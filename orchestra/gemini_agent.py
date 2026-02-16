from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError

import json
from datetime import datetime

from agent_configurations import Agent_Configurations

class Gemini_Agent():
    def __init__(self, lst_prefared_models : list, json_config_file : json, agent_name : str):
        #Agent Specifications
        self.configurations = Agent_Configurations(agent_name=agent_name, prefared_models=lst_prefared_models, json_config_file=json_config_file)
        self.client = genai.Client()
        self.selected_model = self._get_available_model()
        self.session = None
        self.agent_status = False
        self.google_config = None
        
        #Question and Response
        self.sent_content = None
        self.token_count = None
        self.response = None
    
    def update_active_model(self, new_model : str):
        self.selected_model = new_model
        
    def update_active_state(self, current_state : bool):
        self.acitive_state = current_state
        
    def _format_content(self, content):
        formatted_data = {
            "user_query": content,
            "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(formatted_data, indent=4)
        
    def update_sent_content(self, new_content : str):
        self.sent_content = self._format_content(new_content)  
        
    def update_response(self, new_response : types.GenerateContentResponse):
        self.response = new_response  
        
    def extract_reponse_text(self : types.GenerateContentResponse):
        return self.response.text
        
    def _get_available_model(self) -> str:
        #Gets available model based prefarred model selection
        available_models = [m.name for m in self.client.models.list() if 'generateContent' in m.supported_actions]
        
        for preferred in self.preferred_models:
            
            for model_name in available_models:
                
                if model_name.startswith(f"models/{preferred}") or model_name == preferred:
                    self.selected_model = model_name
                    self.is_active = True
                    return model_name
        
        print(f"ERROR: No suitable model found for {self.agent_name}")
        return None    
    
    def _refresh_google_config_object(self) -> types.GenerateContentConfig:
        #Makes config object
        generation_config = types.GenerateContentConfig(
            system_instruction=self.configurations.system_instructions,
            max_output_tokens=self.configurations.max_output_tokens,
            temperature=self.configurations.temperature,
            top_p=self.configurations.top_p,
            top_k=self.configurations.top_k
        )

        return generation_config
    
    def _create_session(self):
        #Initialize all agent features
        self.session = self.client.chats.create(
                        model=self.selected_model,
                        config=self.google_config
                    )
    
    def check_agent_status(self) -> str:
        if self.acitive_state is False:
                return f"Agent: {self.configurations.agent_name} is offline."
    
    def get_sent_content(self) -> json:
        return self.sent_content
    
    def get_token_count(self) -> float:
        return self.token_count
    
    def update_token_count(self, new_amount : float):
        self.token_count = new_amount
    
    def determine_content_tokens(self, text : str):
        response = self.client.models.count_tokens(
            model=self.selected_model,
            contents=text
        )
        tokens =  response.total_tokens
        
        if tokens is None:
            return "There are no tokens generated."
        
        if tokens > self.max_output_tokens:
            return f"Sent content exceeds current max token count. Aborting request."
    
        self.update_token_count(tokens)
        return None
            
    def send_text_message(self, sent_content : json) -> json:
        err_status = self.determine_content_tokens(self.sent_content.get("user_query", None))
        if err_status:
            return err_status

        #Sends json format content to llm
        try:
            response_object = self.session.send_message(sent_content)
            return self.extract_reponse_text(response_object)
        
        except APIError as e:
            return f"An API error has occured : {e}"
        
        except (ClientError, ServerError) as e:
            return f"An Client or Server error has occured : {e}"