from pathlib import Path

PROJECT_BASE_DIR =  Path(__file__).resolve().parent

#Agent Files
ORCHESTRATOR_SETUP_FILE = PROJECT_BASE_DIR / "agents" / "orchestrator" / "orchestrator_config.json"
GENERAL_SETUP_FILE = PROJECT_BASE_DIR / "agents" / "general" / "general_configs.json"
RESEARCHER_SETUP_FILE = PROJECT_BASE_DIR / "agents" / "researcher" / "researcher_config.json"
        
