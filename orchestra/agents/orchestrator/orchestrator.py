import json
from datetime import datetime
from pathlib import Path

from orchestra.gemini_agent import Gemini_Agent
from orchestra.agent_configurations import Agent_Configurations

class Orchestrator(Gemini_Agent):
    def __init__(self, configs : Agent_Configurations):
        super().__init__(configs)
        self._task_file_path = None
        self.task = None
        self.agents = list[str]
        
    def determine_agent_tasks(self):
        response = self.send_text_message(self.get_sent_content())
        self.set_sent_content(response)
        
    def _encountered_error(function_name : str, error_msg : str) -> str:
        return f"Error in {function_name} : {error_msg}"
    
    @property
    def agent(self) -> list:
        return self.agents
    
    def add_to_agent_list(self, agent : str):
        self.agents.append(agent)
        
    @property
    def task(self) -> str:
        return self.task
    
    @task.setter
    def set_task(self, task : str):
        self.task = task
        
    @property
    def task_file_path(self) -> str:
        return self.task_file_path
        
    @task_file_path.setter     
    def _set_task_file_path(self, new_path : Path):
        self.task_file_path = new_path
      
    @property   
    def _updated_tasks(self) -> json:
        formatted_tasks = {
            "tasks": f"{self.task()}",
            "selected_agents": f"{self.agents()}",
            "sent_at": f"{datetime.now()}"
        }
        
        return json.dumps(formatted_tasks)
    
    @property
    def _ensure_file_exists(self):
        #Check if the file already exists
            file_path = Path("..", "tasks.json")
            
            #Creates file if not there
            if not file_path.exists():
                Path.touch()
                self.update_task_file_path(file_path)
                
        
    def build_task_file(self) -> bool:
        try:
            self._ensure_file_exists()
            
            #Add tasks to file
            with open(self.task_file_path, "w", encoding="utf-8") as f:
                self._extract_task()
                self._extract_agents()
                f.write(self._updated_tasks())
             
            #Show operation is successfull   
            return True
                
        except Exception as e:
            self._encountered_error(self.build_task_file.__name__, e)
            return False
        
    def _extract_agents(self):
        try:
            agent_list = self.get_sent_content().get('agents', None)
            for agent in agent_list.split():
                self.add_to_agent_list(agent)
                
        except Exception as e:
            self._encountered_error(self._extract_agents.__name__, e)
            
    def _extract_task(self):
        try:
            self.task = self.get_sent_content().get('agents', None)
                
        except Exception as e:
            self._encountered_error(self._extract_task.__name__, e)