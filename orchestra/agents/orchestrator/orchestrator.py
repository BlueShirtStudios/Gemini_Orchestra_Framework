import json
from datetime import datetime
from pathlib import Path

from orchestra.gemini_agent import Gemini_Agent
from orchestra.agent_configurations import Configurations

class Orchestrator(Gemini_Agent):
    def __init__(self, configs : Configurations):
        super().__init__(configs)
        self._task_file_path = None
        self._task = None
        self._agents = []
        
    def determine_agent_tasks(self):
        response = self.send_text_message()
        self.sent_content = response
    
    @property
    def agents(self) -> list:
        return self._agents
    
    def add_to_agent_list(self, agent : str):
        self._agents.append(agent)
        
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
    def _updated_tasks(self) -> str:
        formatted_tasks = {
            "tasks": f"{self.task}",
            "selected_agents": f"{self.agents}",
            "sent_at": f"{datetime.now()}"
        }
        return json.dumps(formatted_tasks)
    
    def _ensure_file_exists(self):
        file_path = Path("..", "tasks.json")
        
        if not file_path.exists():
            file_path.touch()
            self.task_file_path = file_path
        
    def build_task_file(self):
        try:
            self._ensure_file_exists()
            
            with open(self.task_file_path, "w", encoding="utf-8") as f:
                self._extract_task()
                self._extract_agents()
                f.write(self._updated_tasks)
             
        except Exception as e:
            self._encountered_error(self.build_task_file.__name__, e)
        
    def _extract_agents(self):
        try:
            content = json.loads(self.sent_content) if isinstance(self.sent_content, str) else self.sent_content
            agent_list = content.get('agents', None)
            if agent_list:
                for agent in agent_list.split():
                    self.add_to_agent_list(agent)
                
        except Exception as e:
            self._encountered_error(self._extract_agents.__name__, e)
            
    def _extract_task(self):
        try:
            content = json.loads(self.sent_content) if isinstance(self.sent_content, str) else self.sent_content
            self.task = content.get('task', None)
                
        except Exception as e:
            self._encountered_error(self._extract_task.__name__, e)