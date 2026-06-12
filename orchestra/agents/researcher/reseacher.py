from pathlib import Path

from orchestra.base.gemini_agent import Gemini_Agent
from orchestra.base.agent_configurations import Configurations
from orchestra.agents.researcher.researcher_prompts import ResearcherPrompts
from plp_library.main_library import Document_Library

class Researcher(Gemini_Agent):
    def __init__(self, agent_configs : Configurations):
        super().__init__(agent_configs)
        self._result_dict = dict()
        self._library = Document_Library()
        self._ai_assisted_search = False
        self._prompt_manager = ResearcherPrompts()
        self._query = None
        
        self._initialize_library()
    
    @property
    def results_dict(self) -> dict:
        return self._result_dict
    
    @results_dict.setter
    def results_dict(self, val: dict):
        self._result_dict = val
        
    @property
    def library(self) -> Document_Library:
        return self._library
    
    @property
    def ai_assited_search(self) -> bool:
        return self._ai_assisted_search
    
    @ai_assited_search.setter
    def ai_assited_search(self, val : bool):
        self._ai_assisted_search = val
        
    @property
    def prompt_manager(self) -> str:
        return self._prompt_manager
    
    @property
    def query(self) -> str:
        return self._query
    
    @query.setter
    def query(self, val: str):
        self._query = val
    
    def _initialize_library(self):
        self.library.toggle_result_format_toDict(True)
    
    def add_document_to_library(self, paths: list[str]):
        for file in paths:
            try:
                self.library.add_new_document(file)
                
            except:
                continue
            
    def _scan_library(self):
        self.library.search_library(self.sent_content)
        self.results_dict = self.library.retrieve_results()
        
    def _give_results_to_reseacher(self):
        self.prompt_manager.query = self.query
        built_message = self.prompt_manager.deliver_results(self.results_dict)
        self.execute_stream_payload(built_message)
    
    def search(self) -> any:
        if self._ai_assisted_search:
            pass
            
        else:
            self._scan_library()
            response = self._give_results_to_reseacher()
            
        return response