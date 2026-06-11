from pathlib import Path

from orchestra.base.gemini_agent import Gemini_Agent
from orchestra.base.agent_configurations import Configurations
from document_support.main_library import Document_Library
from orchestra.agents.researcher.researcher_prompts import ResearcherPrompts

class Researcher(Gemini_Agent):
    def __init__(self, agent_configs : Configurations):
        super().__init__(agent_configs)
        self._research_keywords = set()
        self._result_dict = dict()
        self._library = Document_Library()
        self._ai_assisted_search = False
        self._prompt_manager = ResearcherPrompts()
        
        self._initialize_library()
        
    @property
    def research_keywords(self) -> set:
        return self._research_keywords
    
    @research_keywords.setter
    def keywords(self, new_query : str):
        keywords = set()
        for word in new_query.split():
            if len(word) > 3:
                keywords.add(word)
                
        self.research_keywords = keywords
    
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
        self.results = self.library.retrieve_results()
        
    def _give_results_to_reseacher(self):
        self.send_text_message(self.prompt_manager.deliver_results(self.results_dict))
        
    def _search_with_researcher_assit(self):
        pass
    
    def search(self):
        if self._ai_assisted_search:
            self._search_with_researcher_assit()
            
        else:
            self._scan_library()
            self._give_results_to_reseacher()