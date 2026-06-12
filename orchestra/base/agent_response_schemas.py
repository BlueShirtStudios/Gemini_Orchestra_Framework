from pydantic import BaseModel, Field

class Orchestrator_Schema(BaseModel):
    tasks: str = Field(description="The primary objective or step determined by the orchestrator.")
    selected_agents: list[str] = Field(description="List of specific agent names required to execute this task.")