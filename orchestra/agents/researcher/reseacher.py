from pathlib import Path

from orchestra.base.gemini_agent import Gemini_Agent
from orchestra.base.agent_configurations import Configurations
import document_support

class Researcher(Gemini_Agent):
    def __init__(self, agent_configs : Configurations):
        super().__init__(agent_configs)
        self._research_keywords = set()
        self._result_dict = dict()
        self._library = None
        
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
        
    def assign_documents(self, documents : str):
        pass
            
    def _format_result(self, indexs_to_format : list[int]):
        result_counter = 0
        for index in indexs_to_format:
            result_counter =+ 1
            document = self.provided_docs[index]
            self.result_dict = {f"Result {result_counter}" : f"{document.result}"}
            
    def scan_documents(self, query : str, doc_scan_limit : int = 5):
        #Defines what we need
        result_in_docs : list[int]
        index = 0
        
        #Updates query
        self.set_query(query)
        
        #Scans all provided documents in the list
        for document in self.provided_docs:
            #Stops scan if results are found more than limit
            if len(result_in_docs) < doc_scan_limit:
                break
            
            document.search_by_keyword(self.research_keywords)  
            if document.result is None:
                index =+ 1
                continue
            
            result_in_docs.append(index)  
            index =+ 1   
            
        self.format_result(result_in_docs)
        
    def give_research_result(self) -> str:
        return self.send_dict_message(self.result_dict)