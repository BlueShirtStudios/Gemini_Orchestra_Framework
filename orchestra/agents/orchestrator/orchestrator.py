import json
from datetime import datetime
from pathlib import Path

from orchestra.gemini_agent import Gemini_Agent

class Orchestrator(Gemini_Agent):
    def __init__(self, prefarred_models : list, config_file: json, agent_name : str):
        super.__init__(prefarred_models, config_file, agent_name)
        self.given_query = None
        self.jsonified_query = None
        self.task_file_path = None
        self.task_format = None
        
    def update_query(self, new_query : str):
        self.given_query = new_query
        
    def format_query(self):
        formatted_data = {
            "user_query": self.given_query,
            "sent_at": datetime.now()
        }
        
        self.jsonified_query = json.dumps(formatted_data, indent=4)
        
    def determine_agent_tasks(self):
        self.format_query()
        response = self.send_text_message(self.jsonified_query)
        self.update_response(response)
        
    def update_task_file_path(self, new_path : Path):
        self.task_file_path = new_path
        
    def update_tasks(self):
        formatted_tasks = {
            "given_query": {self.given_query},
            "query_tokens": {self.get_token_count(self.given_query)},
            "selected_agents": {self.response.text},
            "sent_at": {datetime.now()}
        }
        
        self.task_format = json.dumps(formatted_tasks)
        
    def add_to_task_file(self) -> bool:
        try:
            #Check if the file already exists
            file_path = Path("..", "tasks.json")
            self.update_task_file_path(file_path)
            if not Path.exists():
                Path.touch()
                
            #Update the tasks
            self.update_tasks()
            
            #Add tasks to file
            with open(self.task_file_path, "w", encoding="utf-8") as f:
                f.write(self.task_format)
                
            return True
                
        except Exception as e:
            return False