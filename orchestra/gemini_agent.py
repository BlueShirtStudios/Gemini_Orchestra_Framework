from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError, ServerError

import json

class Gemini_Agent():
    def __init__(self, lst_prefared_models : list, json_config_file, agent_name : str):
        #Model Details
        self.prefared_models = lst_prefared_models
        self.selected_model = None
        self.client = genai.Client()
        self.session = None
        self.acitive_state = False
        self.agent_name = agent_name
        
        #Agent Parameters
        self.custom_configs_file = json_config_file
        self.system_instructions = None
        self.max_output_tokens = None
        self.temprature = None
        self.top_p = None
        self.top_k = None
        self.google_config = self._create_google_config_object()
    
    def update_active_model(self, new_model : str):
        self.selected_model = new_model
        
    def update_active_state(self, current_state : bool):
        self.acitive_state = current_state
        
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
            
    def _initialize_agent_parameters(self):   
        #Extract all configs from the file and create the generation config
        self.system_instructions = self.config_file.get("system_prompt", None)
        self.max_output_tokens= self.config_file.get("max_output_tokens", 1000)
        self.temperature= self.config_file.get("temperature", 0.7)
        self.top_p = self.config_file.get("top_p", 0.1)
        self.top_k = self.config_file.get("top_k", 40)     
    
    def _refresh_google_config_object(self) -> types.GenerateContentConfig:
        #Makes config object
        generation_config = types.GenerateContentConfig(
            system_instruction=self.system_instructions,
            max_output_tokens=self.max_output_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k
        )

        return generation_config
    
    def update_system_instructions(self, new_instructions : str):
        self.system_instructions = new_instructions
        
    def update_max_output_tokens(self, new_max : int):
        self.max_output_tokenss = new_max
        
    def update_temperature(self, new_temp : float):
        self.temperature = new_temp
        
    def update_top_p(self, new_p : float):
        self.top_p = new_p
        
    def update_top_k(self, new_k : float):
        self.top_k = new_k
    
    def _create_session(self):
        #Initialize all agent features
        self.session = self.client.chats.create(
                        self.selected_model,
                        self.google_config
                    )
        
    def agent_check(self) -> bool:
        #Check if agent is ready for run
        #Checks if model is found and provides feedback
        if self.acitive_state is False:
            self.prefared_models.pop(0)
            self._get_available_model(self.prefared_models)
            
            if self.acitive is False:
                return False
        
        #Creates session if needed
        if self.session is None:
            self._create_session()
            
        return True
    
    def get_token_count(self, text: str) -> int:
        response = self.client.models.count_tokens(
            model=self.selected_model,
            contents=text
        )
        
        return response.total_tokens
            
    def send_text_message(self, sent_content : json) -> json:
        #Checks if content can be asked
        if self.get_token_count(sent_content) > self.max_output_tokens:
            return f"Sent content exceeds current max token count. Aborting request."
        
        #Sends json format content to llm
        try:
            response_object = self.session.send_message(sent_content)
            return response_object
        
        except APIError as e:
            return f"An API error has occured : {e}"
        
        except (ClientError, ServerError) as e:
            return f"An Client or Server error has occured : {e}"