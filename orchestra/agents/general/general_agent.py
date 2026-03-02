from orchestra.gemini_agent import Gemini_Agent
from orchestra.agent_configurations import Agent_Configurations

class General_Agent(Gemini_Agent):
    def __init__(self, agent_configs : Agent_Configurations):
        super().__init__(agent_configs)