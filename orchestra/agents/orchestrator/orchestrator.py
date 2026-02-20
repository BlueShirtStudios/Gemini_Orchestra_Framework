import json
from datetime import datetime
from pathlib import Path

from orchestra.gemini_agent import Gemini_Agent
from orchestra.agent_configurations import Agent_Configurations

class Orchestrator(Gemini_Agent):
    def __init__(self, configs : Agent_Configurations):
        super().__init__(configs)
        self.task_file_path = None
        
    def determine_agent_tasks(self):
        response = self.send_text_message(self.get_sent_content())
        self.set_sent_content(response)
        
    def _update_task_file_path(self, new_path : Path):
        self.task_file_path = new_path
        
    def _updated_tasks(self) -> json:
        formatted_tasks = {
            "given_query": f"{self.get_sent_content()}",
            "query_tokens": f"{self.get_token_count()}",
            "selected_agents": f"{self.response.text}",
            "sent_at": f"{datetime.now()}"
        }
        
        return json.dumps(formatted_tasks)
    
    def does_file_exists(self):
        #Check if the file already exists
            file_path = Path("..", "tasks.json")
            #Creates file if not there
            if not file_path.exists():
                Path.touch()
                self.update_task_file_path(file_path)
                
        
    def build_task_file(self) -> bool:
        try:
            self.does_file_exists()
            
            #Add tasks to file
            with open(self.task_file_path, "w", encoding="utf-8") as f:
                f.write(self._updated_tasks())
                
            return True
                
        except Exception as e:
            print(f"oops : {e}")
            return False