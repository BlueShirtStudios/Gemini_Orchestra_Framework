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
        self.task = None
        self.agents = None
        self.file_loading_enabled = False
        
        #Default Agent Line-up
        self.orchestrator = None
        self.general = None
        self.researcher = None
        
        #Plug and play call order
        self.call_dict = dict()
        
    def enable_file_loading(self):
        self.file_loading_enabled = True     
        
    def create_orchestrator(self, prefarred_models : list, config_file : json):
        orchestrator_configurations = Agent_Configurations(
                agent_name="Orchestrator",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        self.orchestrator = Orchestrator(orchestrator_configurations)  
        
    def create_general(self, prefarred_models : list, config_file : json):
        general_configurations = Agent_Configurations(
                agent_name="General",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        self.general = General_Agent(general_configurations)  
        
    def create_researcher(self, prefarred_models : list, config_file : json):
        researcher_configurations = Agent_Configurations(
                agent_name="Researcher",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        self.researcher = Researcher(researcher_configurations)    
        
    def enable_orchestrasion(self):
        self.engine_mode = self.engine_modes.Orchestration.name
        
    def set_query(self, new_query : str):
        self.query = new_query
        
    def _readTaskFile(self):
        with open(self.orchestrator.task_file_path, "r", encoding="utf-8") as f:
            tasks = json.dumps(f)
            self.task = tasks.get("tasks", None)
            self.agents = tasks.get("agents", None)
            
    def _run_orchestrator(self):
        self.orchestrator.set_sent_content(self.query)
        self.orchestrator.determine_agent_tasks()
        if self.orchestrator.build_task_file():
            pass
        
    def _run_general(self) -> str:
        self.general.set_sent_content(self.query)
        self.general.send_text_message(self.general.get_sent_content())
        return self.general.extract_reponse_text()
        
    def _run_researcher(self) -> str:
        self.researcher.scan_documents(self.query)
        self.researcher.give_research_result()
        return self.researcher.extract_reponse_text()
    
    def build_default_agent_dict(self):
        #Save function location to call dynamicly
        self.call_dict = {
            "general": self._run_general,
            "researcher": self._run_researcher
        }
        
    def _read_from_orchestrator(self):
        self.task = self.orchestrator.task
        self.agents = self.orchestrator.agents
            
    def prepare_for_run(self):
        #Checks if all agents are ready 
        #Check Orchestrator
        if isinstance(self.orchestrator) is None:
            print(self.orchestrator.check_agent_status())
            if self.orchestrator.agent_status is False:
                return self.orchestrator.agent_offline_msg()
            
            #Check General
            if isinstance(self.general) is None:
                print(self.general.check_agent_status())
                if self.general.agent_status is False:
                    return self.general.agent_offline_msg()
                
                #Check Researcher
                if isinstance(self.researcher) is None:
                    print(self.researcher.check_agent_status())
                    if self.researcher.agent_status is False:
                        return self.researcher.agent_offline_msg()
                    
        #Build Agent Dict
        self.build_default_agent_dict()
        
    def _call_agent(self, agent : str):
        try:
            self.call_dict[agent]()
            
        except Exception as e:
            self.engine_function_error_msg(self.call_agent.__name__, e)
            
    def  _run_selected_agents(self):
        for agent in self.agents:
            for key in self.call_dict:
                if agent == key:
                    self.call_dict[key]()
                
                
    def start_orchestration(self):
        #Run the orchestrator to determine agent tasks
        self._run_orchestrator()
        
        #Let the call order be defined
        try:
            self._readTaskFile()
        except Exception as e:
            print(self.engine_function_error_msg(self._readTaskFile.__name__, e))
            self._read_from_orchestrator()
            
        #
            
    def engine_function_error_msg(function_name : str, error : str):
        return f"Error at {function_name}, Error : {error}"