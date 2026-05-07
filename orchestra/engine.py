#Python Imports
import json
from pathlib import Path

#Config Imports
from orchestra.project_configs import PROJECT_BASE_DIR, ORCHESTRATOR_SETUP_FILE, GENERAL_SETUP_FILE, RESEARCHER_SETUP_FILE

#Custom import collection
from orchestra.agent_configurations import Configurations
from orchestra.agents.orchestrator.orchestrator import Orchestrator
from orchestra.agents.general.general_agent import General_Agent
from orchestra.agents.researcher.reseacher import Researcher
from orchestra.engine_modes import EngineModes

class Orchestration_Engine():
    def __init__(self):
        #Engine Details
        self.engine_modes = EngineModes
        self.engine_mode = None
        
        #Default Agent Line-up
        self.orchestrator = None
        self.general = None
        self.researcher = None
        
        #Orchestration Details
        self.query = None
        self.task = None
        self.agents = None
        self.response_text = None
        self.call_dict = dict() 
        
    def enable_orchestrasion(self):
        self.engine_mode = self.engine_modes.Orchestration.name
        
    def set_query(self, new_query : str):
        self.query = new_query
        
    def prepare_engine(self):
        #Check what options are toggled
        #Orchestration Run
        if self.engine_mode == self.engine_modes.Orchestration.name:
            self._build_default_agent_dict()
            self._ensure_all_orchrestration_agent_active()
            
        
    def create_orchestrator(self, prefarred_models : list):
        #Create a config object for the orchestrator
        orchestrator_configurations = Configurations(
                agent_name="Orchestrator",
                prefared_models=prefarred_models,
                json_config_file=ORCHESTRATOR_SETUP_FILE
        )
        
        #Create an instance of the Orchestrator Class
        self.orchestrator = Orchestrator(orchestrator_configurations, PROJECT_BASE_DIR)  
        
    def create_general(self, prefarred_models : list):
        #Create a config object for the general agent
        general_configurations = Configurations(
                agent_name="General",
                prefared_models=prefarred_models,
                json_config_file=GENERAL_SETUP_FILE
        )
        
        #Create an instance of the General Agent
        self.general = General_Agent(general_configurations)  
        
    def create_researcher(self, prefarred_models : list):
        #Create a config for the researcher agent
        researcher_configurations = Configurations(
                agent_name="Researcher",
                prefared_models=prefarred_models,
                json_config_file=RESEARCHER_SETUP_FILE
        )
        
        #Create an instance of the researcher agent
        self.researcher = Researcher(researcher_configurations)    
        
    def _read_task_file(self):
        #Reads the generated task file and extracts the details
        with open(self.orchestrator.task_file_path, "r", encoding="utf-8") as f:
            tasks = json.load(f)
            if tasks is not None:
                self.task = tasks.get("tasks", None)
                self.agents = tasks.get("selected_agents", None)
            
    def _run_orchestrator(self):
        self.orchestrator.sent_content = self.query
        self.orchestrator.determine_agent_tasks()
        self.orchestrator.write_to_task_file() 
        
    def _run_general(self) -> str:
        self.general.sent_content = self.query
        self.general.send_text_message()
        self.response_text = self.general.read_only_reponse_text()
        
    def _run_researcher(self) -> str:
        self.researcher.sent_content = self.response_text
        self.researcher.scan_documents()
        self.researcher.give_research_result()
        self.response_text = self.researcher.read_only_reponse_text()
    
    def _build_default_agent_dict(self):
        #Save function location to call dynamicly
        self.call_dict = {
            "GENERAL_AGENT": self._run_general,
            "RESEARCHER": self._run_researcher
        }
        
    def _read_from_orchestrator(self):
        self.task = self.orchestrator.task
        self.agents = self.orchestrator.agents
        
    def _ensure_all_orchrestration_agent_active(self):
        pass
        #tackle this later
        
    def _call_agent(self, agent : str):
        try:
            self.call_dict[agent]()
            
        except Exception as e:
            self.engine_function_error_msg(self._call_agent.__name__, e)
            
    def _run_selected_agents(self):
        for agent in self.agents:
            if agent in self.call_dict:
                self.call_dict[agent]()
                
    def start_orchestration(self):
        #Run the orchestrator to determine agent tasks
        self._run_orchestrator()
        
        #Let the call order be defined
        try:
            self._read_task_file()
            
        except Exception as e:
            print(self.engine_function_error_msg(self._read_task_file.__name__, e))
            
            #Fallback emergency method if the file fails
            self._read_from_orchestrator()
            
        #Run the agents
        self._run_selected_agents()
            
    def engine_function_error_msg(self, function_name : str, error : str):
        return f"Error at {function_name}, Error : {error}"
    
    def add_research_document(self, str_path : str):
        pass