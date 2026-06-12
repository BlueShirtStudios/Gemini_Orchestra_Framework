import json
from pathlib import Path

from orchestra.base.gemini_agent import Gemini_Agent
from orchestra.base.agent_configurations import Configurations

class Orchestrator(Gemini_Agent):
    def __init__(self, configs : Configurations, BASE_DIR_FOR_TASK_FILE : Path):
        super().__init__(configs)
        self._BASE_DIR = BASE_DIR_FOR_TASK_FILE
        self._task_file_path = BASE_DIR_FOR_TASK_FILE / "task_file_test.json"
        self._task = None
        self._agents = []
        
    @property
    def agents(self) -> list:
        return self._agents
    
    @agents.setter
    def agents(self, list : list):
        for i in range(0, len(list)):
            self._agents.append(list[i])
        
    @property
    def task(self) -> str:
        return self._task
    
    @task.setter
    def task(self, task : str):
        self._task = task
        
    @property
    def task_file_path(self) -> str:
        return self._task_file_path
        
    @task_file_path.setter     
    def task_file_path(self, new_path : Path):
        self._task_file_path = new_path
    
    @property
    def BASE_DIR(self) -> Path:
        return self._BASE_DIR
    
    @BASE_DIR.setter
    def BASE_DIR(self, path : Path):
        self._BASE_DIR = path
    
    def determine_agent_tasks(self, query: str):
        try:
            #Send to Agent to get the agent call
            json_response = self.send_small_payload(query)
            json_response = json.loads(json_response)
            
            #Read the details from the response
            self.task = json_response.get("tasks", None)
            self.agents = json_response.get("selected_agents", None)
            
        except json.JSONDecodeError as e:
            self._encountered_error(self.determine_agent_tasks.__name__, e)
                
        except Exception as e:
            self._encountered_error(self.determine_agent_tasks.__name__, e)
    
    def _ensure_file_exists(self):
        #Create a default path for the task file
        if not self.task_file_path.exists():
            file_path = self.BASE_DIR / "task_file.json"
            file_path.touch()
            self.task_file_path = file_path
        
    def write_to_task_file(self, content: json):
        try:
            self._ensure_file_exists()
            
            #Writes formatted response to file
            with open(self.task_file_path, "w", encoding="utf-8") as f:
               json.dump(content, f, indent=4)
             
        except Exception as e:
            self._encountered_error(self.write_to_task_file.__name__, e)