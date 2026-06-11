class ResearcherPrompts():
    def __init__(self):
        self._query = None
    
    def deliver_results(self, founding: dict) -> str:
        return f"""
        Here are the search results based on the keywords {self.query} search we did. Take the provided information
        and answer the question to the best of your capabilities:
        
        Relavant Results: {founding}
       
        """
        
    def get_the_file_schema(self, schema: dict) -> str:
        return f"""
        This is how the file layout/schema looks like
        
        Schema : {schema}
        """
        
    def assit_with_search(self) -> str:
        return """
        You are going to help with deciding how we search. You have 
        """
        #Revist this...
    