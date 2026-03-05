#Custom import collection
from orchestra.agent_configurations import Agent_Configurations
from orchestra.agents.orchestrator.orchestrator import Orchestrator
from orchestra.agents.general.general_agent import General_Agent
from orchestra.agents.researcher.reseacher import Researcher

from orchestra.engine_modes import EngineModes

import json

class Orchestration_Engine():
    def __init__(self):
        #Engine Details
        self.engine_modes = EngineModes()
        self.engine_mode = None
        self.query = None
        
        #Default Agent Line-up
        self.orchestrator = None
        self.general = None
        self.researcher = None
        
        
    def create_orchestrator(self, prefarred_models : list, config_file : json):
        orchestrator_configurations = Agent_Configurations(
                agent_name="Orchestrator",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        self.orchestrator = Orchestrator(orchestrator_configurations)  
        
    def create_general(self, prefarred_models : list, config_file : json):
        orchestrator_configurations = Agent_Configurations(
                agent_name="General",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        self.general = Orchestrator(orchestrator_configurations)  
        
    def create_researcher(self, prefarred_models : list, config_file : json):
        orchestrator_configurations = Agent_Configurations(
                agent_name="Researcher",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        self.researcher = Orchestrator(orchestrator_configurations)    
        
    def enable_orchestrasion(self):
        self.engine_mode = self.engine_modes.Orchestration.name
        


