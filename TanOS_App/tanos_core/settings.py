# tanos_core/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Paths ---
# Assumes tanos_prompts and tanos_data are at the same level as tanos_core
# Adjust if your MEMORIES and TanOS_Prompts are elsewhere.
# It's recommended to copy/symlink them into the TanOS_App structure for deployment.
TANOS_PROMPTS_DIR = os.getenv("TANOS_PROMPTS_DIR", str(BASE_DIR / "tanos_prompts"))
TANOS_DATA_DIR = os.getenv("TANOS_DATA_DIR", str(BASE_DIR / "tanos_data"))

MEMORIES_DIR = Path(TANOS_DATA_DIR) / "memories"
OPERATIONAL_STATE_DIR = Path(TANOS_DATA_DIR) / "operational_state"
CHANGELOGS_DIR = Path(TANOS_DATA_DIR) / "changelogs"

# --- LLM Configuration ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")  # 'openai', 'anthropic', 'ollama', 'local_gguf', 'mock'
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")
# Add other LLM specific settings as needed

# --- Application Settings ---
DEFAULT_USER = "Tan"
CURRENT_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"

# Create data directories if they don't exist
MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
OPERATIONAL_STATE_DIR.mkdir(parents=True, exist_ok=True)
CHANGELOGS_DIR.mkdir(parents=True, exist_ok=True)

# --- Tan-Specific Thresholds (Example - to be loaded from a config or MEMORIES) ---
# These would ideally be loaded from a user-configurable part of MEMORIES
# or a dedicated settings file within tanos_data.
TAN_HRV_YELLOW_FLAG_CONDITION = "< 45ms for 2 consecutive days" # Example string
TAN_SLEEP_YELLOW_FLAG_CONDITION = "< 6/10 for 2 consecutive nights" # Example string

if __name__ == '__main__':
    print(f"Base Directory: {BASE_DIR}")
    print(f"TanOS Prompts Directory: {TANOS_PROMPTS_DIR}")
    print(f"TanOS Data Directory: {TANOS_DATA_DIR}")
    print(f"Memories Directory: {MEMORIES_DIR}")
    print(f"Operational State Directory: {OPERATIONAL_STATE_DIR}")
    print(f"Changelogs Directory: {CHANGELOGS_DIR}")
    print(f"LLM Provider: {LLM_PROVIDER}")
