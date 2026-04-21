#Custom import collection
from orchestra.agent_configurations import Configurations
from orchestra.agents.orchestrator.orchestrator import Orchestrator
from orchestra.agents.general.general_agent import General_Agent
from orchestra.agents.researcher.reseacher import Researcher
from orchestra.engine_modes import EngineModes

#Python Imports
import json
from pathlib import Path

class Orchestration_Engine():
    def __init__(self):
        #Engine Details
        self.engine_modes = EngineModes
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
        
    def create_orchestrator(self, prefarred_models : list):
        #Full directory from running file to configs
        BASE_DIR = Path(__file__).resolve().parent
        config_file = BASE_DIR / "agents" / "orchestrator" / "orchestrator_config.json"
        
        #Create a config object for the orchestrator
        orchestrator_configurations = Configurations(
                agent_name="Orchestrator",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        
        #Create an instance of the Orchestrator Class
        self.orchestrator = Orchestrator(orchestrator_configurations)  
        
    def create_general(self, prefarred_models : list):
        #Full directory from running file to configs
        BASE_DIR = Path(__file__).resolve().parent
        config_file = BASE_DIR / "agents" / "general" / "general_configs.json"
        
        #Create a config object for the general agent
        general_configurations = Configurations(
                agent_name="General",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        
        #Create an instance of the General Agent
        self.general = General_Agent(general_configurations)  
        
    def create_researcher(self, prefarred_models : list):
        #Full directory from running file to configs
        BASE_DIR = Path(__file__).resolve().parent
        config_file = BASE_DIR / "agents" / "researcher" / "reasearcher_config.json"
        
        #Create a config for the researcher agent
        researcher_configurations = Configurations(
                agent_name="Researcher",
                prefared_models=prefarred_models,
                json_config_file=config_file
        )
        
        #Create an instance of the researcher agent
        self.researcher = Researcher(researcher_configurations)    
        
    def enable_orchestrasion(self):
        self.engine_mode = self.engine_modes.Orchestration.name
        
    def set_query(self, new_query : str):
        self.query = new_query
        
    def _readTaskFile(self):
        with open(self.orchestrator.task_file_path, "r", encoding="utf-8") as f:
            tasks = json.load(f)
            self.task = tasks.get("tasks", None)
            self.agents = tasks.get("agents", None)
            
    def _run_orchestrator(self):
        self.orchestrator.sent_content = self.query
        self.orchestrator.determine_agent_tasks()
        self.orchestrator.build_task_file() 
        
    def _run_general(self) -> str:
        self.general.sent_content = self.query
        self.general.send_text_message()
        
    def _run_researcher(self) -> str:
        self.researcher.scan_documents(self.query)
        self.researcher.give_research_result()
    
    def _build_default_agent_dict(self):
        #Save function location to call dynamicly
        self.call_dict = {
            "general": self._run_general,
            "researcher": self._run_researcher
        }
        
    def _read_from_orchestrator(self):
        self.task = self.orchestrator.task
        self.agents = self.orchestrator.agents
        
    def _ensure_all_orchrestration_agent_active(self):
        pass
        #tackle this later
            
    def _prepare_for_orchestration(self):        
        #Build Agent Dict
        self._build_default_agent_dict()
        
    def _call_agent(self, agent : str):
        try:
            self.call_dict[agent]()
            
        except Exception as e:
            self.engine_function_error_msg(self._call_agent.__name__, e)
            
    def _run_selected_agents(self):
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
            
        #Run the agents
        self._run_selected_agents()
            
    def engine_function_error_msg(self, function_name : str, error : str):
        return f"Error at {function_name}, Error : {error}"