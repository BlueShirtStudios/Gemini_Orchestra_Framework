#Custom import collection
from orchestra.model_config import Orchestrator_Configs
from orchestra.agents.orchestrator.orchestrator import Orchestrator

class Orchestration_Engine():
    def __init__(self):
        self.query = None
        #Orchestrator
        self.cfg_orchestrator = Orchestrator_Configs()
        self.orchestration_agent = Orchestrator(self.cfg_orchestrator.get_models(),
                                  self.cfg_orchestrator.get_config_file(),
                                  self.cfg_orchestrator.get_agent_name()
                                  )
        
    def _intitialize_agents(self):
    #Prepare the orchestration agent
        status = self.orchestration_agent.prepare_for_run() 
        print(status)   
    
    def check_agents(self):
        print(self.orchestration_agent.check_agent_status())
        
    def update_query(self, new_query : str):
        self.query = new_query
        
    def start_performance(self) -> str:
        #Send the query to the orchestration agent    
        self.orchestration_agent.update_sent_content(self.query)
        self.orchestration_agent.determine_agent_tasks()
        if self.orchestration_agent.build_task_file() is False:
            return f"Orchestration Failed: Could not build task file"