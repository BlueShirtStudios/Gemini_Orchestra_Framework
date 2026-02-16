import json
from datetime import datetime
from pathlib import Path

from orchestra.gemini_agent import Gemini_Agent

class Orchestrator(Gemini_Agent):
    def __init__(self, prefarred_models : list, config_file: json, agent_name : str):
        super().__init__(prefarred_models, config_file, agent_name)
        self.task_file_path = None
        
    def determine_agent_tasks(self):
        response = self.send_text_message(self.get_content())
        self.update_response(response)
        
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
            self.update_task_file_path(file_path)
            if not Path.exists():
                Path.touch()
        
    def build_task_file(self) -> bool:
        try:
            self.does_file_exists()
            
            #Add tasks to file
            with open(self.task_file_path, "w", encoding="utf-8") as f:
                f.write(self._updated_tasks())
                
            return True
                
        except Exception as e:
            return False