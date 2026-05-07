from orchestra.engine import Orchestration_Engine
from pathlib import Path

"""
This part only needs to be done once, intializing and creating the engine and agents. Ensure the intialization only happens once
or if manually asked to restart to prevent long loading periods.
"""
#Initialize the Engine
myEngine = Orchestration_Engine()

#Define how you want to use the Engine (this will be expanded on)
myEngine.enable_orchestrasion()

#Initialize each agent you want to use in the orchestration
myEngine.create_orchestrator(
    #Define your models you want the agent to use, the other models will act as a fallback
    prefarred_models=["gemini-2.5-flash", "gemini-2.5-flash-lite"]
)

myEngine.create_general(prefarred_models=["gemini-2.5-flash", "gemini-2.5-flash-lite"])
myEngine.create_researcher(prefarred_models=["gemini-2.5-flash", "gemini-2.5-flash-lite"])

#After defining how you want to use the engine, we prepare it
myEngine.prepare_engine()
    

"""
After the inialization we can feed it the question we need it answer. I will demonstate use in a while loop of input
"""
runApp = True
while runApp:
    question = input("What is your question? ")
    
    #Give the Engine the query
    myEngine.set_query(question)
    
    #Starts the whole process for the orchestration
    myEngine.start_orchestration()
    print("")
    