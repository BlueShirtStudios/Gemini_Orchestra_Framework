from pathlib import Path
import json

class Agent_Config_Controller():
    def __init__(self, model_list : list, config_file : Path, name : str):
        self.agent_models = model_list
        self.config_file = str(config_file)
        self.name = name
        
    def get_models(self) -> list:
        return self.agent_models
    
    def get_config_file(self) -> Path:
        return self.config_file
    
    def get_agent_name(self) -> str:
        return self.name
    
    def load_config_file(self) -> dict:
        content = self.config_file.read_text(encoding='utf-8')
        return json.loads(content)
    
class Orchestrator_Configs(Agent_Config_Controller):
    def __init__(self):
        super().__init__(["gemini-2.5-flash", "gemini-2.5-flash-lite"], 
                    Path("orchestra", "agents", "orchestrator", "orchestrator_config.json"),
                    "Orchestrator")