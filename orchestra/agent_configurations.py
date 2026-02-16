class Agent_Configurations():
    def __init__(self, agent_name, prefared_models : list, json_config_file):
        #Agent Details
        self.agent_name = agent_name
        self.preferred_models = prefared_models
        
        #Agent Parameters
        self.config_file= json_config_file
        self.system_instructions = None
        self.max_output_tokens = None
        self.temprature = None
        self.top_p = None
        self.top_k = None
        self.google_config = None   