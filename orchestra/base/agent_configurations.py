import json
from typing import Optional, Type
from pydantic import BaseModel
from pathlib import Path
from orchestra.project_configs import PROJECT_BASE_DIR

class Configurations():
    def __init__(self, agent_name, prefared_models : list, json_config_file, response_schema: Optional[Type[BaseModel]] = None):
        #Agent Details
        self._agent_name = agent_name
        self._preferred_models = prefared_models
        
        #Agent Parameters
        self._config_file = json_config_file
        self._system_instructions = None
        self._max_payload_tokens = None
        self._max_session_tokens = None
        self._temprature = None
        self._top_p = None
        self._top_k = None  
        self._response_schema = response_schema
        
        #Read the configurations from the file
        self._initialize_agent_parameters()
        
    @property
    def agent_name(self) -> str:
        return self._agent_name
    
    @property
    def preferred_models(self) -> list[str]:
        return self._preferred_models
    
    @preferred_models.setter
    def prefarred_models(self, val: list):
        self.preferred_models = val
        
    @property
    def config_file(self):
        return self._config_file

    @property
    def system_instructions(self):
        return self._system_instructions

    @property
    def max_payload_tokens(self):
        return self._max_output_tokens

    @max_payload_tokens.setter
    def max_payload_tokens(self, value: int):
        self._max_output_tokens = value
        
    @property
    def max_session_tokens(self):
        return self._max_session_tokens

    @max_session_tokens.setter
    def max_session_tokens(self, value : int):
        self._max_session_tokens = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @property
    def top_p(self):
        return self._top_p

    @top_p.setter
    def top_p(self, value):
        self._top_p = value

    @property
    def top_k(self):
        return self._top_k

    @top_k.setter
    def top_k(self, value):
        self._top_k = value

    @property
    def response_schema(self):
        return self._response_schema

    @response_schema.setter
    def response_schema(self, value):
        self._response_schema = value
    
    def _str_to_path(self, str_path: str) -> Path:
        if isinstance(str_path, Path):
            return str_path
        
        current_file_path = PROJECT_BASE_DIR
        parts = [p for p in str_path.split('/') if p]
        
        for part in parts:
            current_file_path = current_file_path / part
            
        return current_file_path
    
    def _initialize_agent_parameters(self): 
        #Format the Path
        self._config_file = self._str_to_path(self.config_file)
        
        #Read all configs from the file
        with open(self._config_file, "r") as f:
            config_data =  json.load(f)
            
        #Read System instruction path from file and convert to path object      
        system_instructions_path = config_data.get("instruction_file", None)
        system_instructions_path = self._str_to_path(system_instructions_path)
        
        #Read the file from the created path object
        if system_instructions_path:
            with open(system_instructions_path, "r", encoding= "utf-8") as f:
                self._system_instructions = f.read()
                
        else:
            self._system_instructions = None
        
        #Assign the rest of the paramaters
        self.max_payload_tokens = config_data.get("max_payload_tokens", 1000)
        self.max_session_tokens = config_data.get("max_session_tokens", 100000)
        self.temperature = config_data.get("temperature", 0.7)
        self.top_p = config_data.get("top_p", 0.1)
        self.top_k = config_data.get("top_k", 40)    