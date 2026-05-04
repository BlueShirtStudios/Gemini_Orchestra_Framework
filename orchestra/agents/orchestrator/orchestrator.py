import json
from datetime import datetime
from pathlib import Path

from orchestra.gemini_agent import Gemini_Agent
from orchestra.agent_configurations import Configurations

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
        self.BASE_DIR = path
    
    def determine_agent_tasks(self):
        try:
            #Send to Agent to get the agent call
            self.send_text_message()
            response_text = self.read_only_reponse_text()
            
            #Take the text and extract the task and the agents required
            tuple_response = self._extract_task_and_agents_from_response(response_text)
            
            #Assign to the respected properties
            self.task = tuple_response[0]
            self.agents = tuple_response[1]
        
        except Exception as e:
            self._encountered_error(self.determine_agent_tasks.__name__, e)
        
    def _extract_task_and_agents_from_response(self, text : str) -> tuple[str, list]:
        #Find both the dashes
        first_dash = text.find('-')
        second_dash = text.find('-', first_dash + 1)
        
        #Check if both dashes actually exist to avoid slicing errors
        if first_dash == -1 or second_dash == -1:
            return "", ""

        #Get the respective parts for both the agent and the task
        tasks = text[first_dash + 1 : second_dash].strip()
        agents = text[second_dash + 1 :].strip()
        
        return self._clean_task(tasks), self._clean_agents(agents)
    
    def _clean_task(self, task : str) -> str:
        colon_pos = task.find(':')
        return task[colon_pos + 1: len(task)].strip()
        
    def _clean_agents(self, agents : str) -> list:
        agent_list = []
        colon_pos = agents.find(':')
        if agents.find(',') is None:
            #If there are more than one callable agent
            new_agent = agents[colon_pos + 1:len(agents)].strip()
            agent_list.append(new_agent)
            agents.replace(new_agent, "")
        
        else:
            #If only one agent is called
            agent = agents[colon_pos + 1:len(agents)].strip()
            agent_list.append(agent)
            
        return agent_list

    def _formatted_tasks(self) -> json:
        formatted_tasks = {
            "tasks": f"{self.task}",
            "selected_agents": f"{self.agents}",
        }
        return json.dumps(formatted_tasks)
    
    def _ensure_file_exists(self):
        #Create a default path for the task file
        file_path = self.BASE_DIR / "tasks_testfile.json"
            
        if not file_path.exists():
            file_path.touch()
            self.task_file_path = file_path
        
    def write_to_task_file(self):
        try:
            self._ensure_file_exists()
            
            with open(self.task_file_path, "w", encoding="utf-8") as f:
                f.write(self._formatted_tasks())
             
        except Exception as e:
            self._encountered_error(self.write_to_task_file.__name__, e)