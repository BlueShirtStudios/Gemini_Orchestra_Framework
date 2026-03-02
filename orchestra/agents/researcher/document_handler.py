from collections import defaultdict
import json

class Document_Handler():
    def __init__(self):
        self.knowledge_file_path = None
        self.data = []
        self.index = defaultdict(list)
        self.result = None
        
    def set_knowledge_file(self, new_knowledge_file_path):
        self.knowledge_file_path = new_knowledge_file_path
        
    def _load_file(self):
        try:
            with open(self.knowledge_file_path, "r", encoding="utf8") as file:
                for line in file:
                    #Add whole file to data
                    entry = json.loads(line)
                    self.data.append(entry)
                
                    #Build Index
                    title = entry.get("title", "").lower()
                    for word in title.split():
                        self.index[word].append(entry)
                        
        except json.JSONDecodeError as e:
            return f"Error has occured: {e}"
        

    def search_by_keyword(self, keywords : set):#This needs an update ASAP
        search_result = []
        unique_results = set()
        
        for word in keywords:
            if not word:
                continue
            
            if word in self.index:
                for entry in self.index[word]:
                    if entry.get("pageid") not in unique_results:
                        unique_results.add(entry.get("pageid"))
                        search_result.append({ 
                                          "pageid": entry.get("pageid", "N/A"), 
                                          "title": entry.get("title", "N/A"), 
                                          "fullurl": entry.get("fullurl", "N/A"),
                                          "thumbnail": entry.get("thumbnail", "N/A"),
                                          "categories": entry.get("categories", "N/A")})
                        
        return search_result