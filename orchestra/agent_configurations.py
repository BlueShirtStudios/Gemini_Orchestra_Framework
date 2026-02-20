import json

class Agent_Configurations():
    def __init__(self, agent_name, prefared_models : list, json_config_file):
        #Agent Details
        self.agent_name = agent_name
        self.preferred_models = prefared_models
        
        #Agent Parameters
        self.config_file= json_config_file
        self.system_instructions = None
        self.max_output_tokens = None
        self.temprature = None
        self.top_p = None
        self.top_k = None  
        
    def _initialize_agent_parameters(self): 
        #Extract all configs from the file
        print(self.config_file) 
        with open(self.config_file, "r") as f:
            config_data =  json.load(f)
            
        #Extract system instructionjs from provided path        
        system_instructions_path = config_data.get("instruction_file", None)
        if system_instructions_path:
            with open(system_instructions_path, "r") as f:
                self.system_instructions = json.load(f)
                
        else:
            self.system_instructions = None
        
        #Assign the rest of the parematers
        self.max_output_tokens= config_data.get("max_output_tokens", 1000)
        self.temperature= config_data.get("temperature", 0.7)
        self.top_p = config_data.get("top_p", 0.1)
        self.top_k = config_data.get("top_k", 40)    
        
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