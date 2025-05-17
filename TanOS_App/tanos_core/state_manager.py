# tanos_core/state_manager.py
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import pytz # for timezone

from . import settings

CAPTAINS_LOG_STATE_FILE = settings.OPERATIONAL_STATE_DIR / "captains_log_state.json"
DEFAULT_LOCATION = "Barcelona, Catalonia, Spain" # Example, Tan can update

class CaptainsLogStateManager:
    """
    Manages the dynamic operational state of Nomad's Captain's Log.
    This includes current date/time, Tan's location, mood/energy, active projects, etc.
    """
    def __init__(self, state_file: Path = CAPTAINS_LOG_STATE_FILE):
        self.state_file = state_file
        self.state: Dict[str, Any] = self._load_or_initialize_state()

    def _load_or_initialize_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    print(f"Loaded Captain's Log state from {self.state_file}")
                    # Ensure essential dynamic fields are updated on load
                    state_data["current_date_time"] = self._get_current_datetime_str()
                    return state_data
            except json.JSONDecodeError:
                print(f"Warning: Error decoding JSON from {self.state_file}. Initializing new state.")
            except Exception as e:
                print(f"Warning: Could not load state from {self.state_file} ({e}). Initializing new state.")
        
        print(f"Initializing new Captain's Log state at {self.state_file}")
        # Initialize with default structure based on Nomad_Core_Persona_and_State.txt
        return {
            "current_date_time": self._get_current_datetime_str(),
            "tan_current_location": DEFAULT_LOCATION,
            "tan_mood_energy_summary": "Neutral, Energy 5/10 (Initial State)",
            "health_metric_flags": "No flags active (Initial State)",
            "active_projects": {}, # Store as dict: {"Project Name": {"status": "...", "milestone": "...", "next_step": "..."}}
            "recent_key_insights": [], # List of {"summary": "...", "date": "..."}
            "pending_decisions": {}, # {"Decision Name": {"transformative_flag": True/False}}
            "nomad_version": "0.3" # Default to current conceptual version
        }

    def _get_current_datetime_str(self) -> str:
        # Example: Use Tan's current location if known, otherwise UTC or a default
        # For now, let's use a fixed timezone for consistency in example.
        # Tan can update his preferred timezone in settings or profile.
        try:
            tz_str = self.state.get("tan_timezone", "Europe/Madrid") # Default if not set
            timezone = pytz.timezone(tz_str)
        except pytz.UnknownTimeZoneError:
            timezone = pytz.utc
            print(f"Warning: Unknown timezone '{tz_str}'. Defaulting to UTC.")
            
        return datetime.now(timezone).strftime(settings.CURRENT_DATETIME_FORMAT)


    def save_state(self) -> None:
        """Saves the current state to the JSON file."""
        try:
            # Always update dynamic fields before saving
            self.state["current_date_time"] = self._get_current_datetime_str()
            # Potentially fetch nomad_version from ChangelogManager if it's dynamic
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=4, ensure_ascii=False)
            print(f"Captain's Log state saved to {self.state_file}")
        except Exception as e:
            print(f"Error saving Captain's Log state to {self.state_file}: {e}")

    def get_state(self) -> Dict[str, Any]:
        """Returns the current state, ensuring dynamic fields are fresh."""
        self.state["current_date_time"] = self._get_current_datetime_str()
        return self.state.copy() # Return a copy to prevent direct modification

    def update_state_variable(self, key: str, value: Any) -> None:
        """Updates a specific variable in the state."""
        if key == "current_date_time":
            print("Warning: current_date_time is updated automatically. Manual update ignored.")
            return
        self.state[key] = value
        print(f"Captain's Log state updated: {key} = {value}")
        self.save_state() # Auto-save on update

    def add_active_project(self, name: str, status: str, milestone: str, next_step: str) -> None:
        self.state.setdefault("active_projects", {})[name] = {
            "status": status, "milestone": milestone, "next_step": next_step
        }
        self.save_state()
        print(f"Project '{name}' added/updated in Captain's Log.")

    def add_insight(self, insight_summary: str) -> None:
        self.state.setdefault("recent_key_insights", []).insert(0, { # Add to beginning
            "summary": insight_summary,
            "date": self._get_current_datetime_str().split(" ")[0] # Just date part
        })
        # Keep only latest N insights if needed (e.g., last 5)
        self.state["recent_key_insights"] = self.state["recent_key_insights"][:5]
        self.save_state()
        print(f"Insight added to Captain's Log: {insight_summary}")

    def update_nomad_version(self, version: str) -> None:
        self.update_state_variable("nomad_version", version)

    def get_formatted_state_for_prompt(self) -> str:
        """Formats the current state into a string suitable for LLM context."""
        current_state = self.get_state()
        # Customize this formatting to match the Captain's Log prompt structure
        # This needs to carefully replace the {{placeholders}} in the prompt
        prompt_str = f"""
Operational State Snapshot (as of {current_state['current_date_time']}):
- Tan's Location: {current_state.get('tan_current_location', 'Unknown')}
- Tan's Reported Mood/Energy: {current_state.get('tan_mood_energy_summary', 'Not reported')}
- Health Metric Flags: {current_state.get('health_metric_flags', 'None')}
- Nomad Conceptual Version: {current_state.get('nomad_version', 'Unknown')}

Active Projects & Focus:
"""
        active_projects = current_state.get("active_projects", {})
        if not active_projects:
            prompt_str += "- No active projects listed.\n"
        for name, details in active_projects.items():
            prompt_str += f"  - Project: {name}\n"
            prompt_str += f"    Status: {details.get('status', 'N/A')}\n"
            prompt_str += f"    Current Milestone: {details.get('milestone', 'N/A')}\n"
            prompt_str += f"    Next Concrete Step: {details.get('next_step', 'N/A')}\n"

        prompt_str += "\nRecent Key Insights/Reflections:\n"
        recent_insights = current_state.get("recent_key_insights", [])
        if not recent_insights:
            prompt_str += "- No recent insights logged.\n"
        for insight in recent_insights:
            prompt_str += f"  - ({insight.get('date', 'N/A')}) {insight.get('summary', 'N/A')}\n"
        
        prompt_str += "\nPending Decisions:\n"
        pending_decisions = current_state.get("pending_decisions", {})
        if not pending_decisions:
            prompt_str += "- No pending decisions listed.\n"
        for name, details in pending_decisions.items():
            transformative_flag = "YES" if details.get("transformative_flag") else "NO"
            prompt_str += f"  - Decision: {name} (Transformative: {transformative_flag})\n"
            
        return prompt_str.strip()

if __name__ == '__main__':
    csm = CaptainsLogStateManager()
    print("\nInitial State:")
    # print(json.dumps(csm.get_state(), indent=2))
    print(csm.get_formatted_state_for_prompt())

    csm.update_state_variable("tan_mood_energy_summary", "Feeling focused, Energy 7/10")
    csm.add_active_project("TanOS App Dev", "In Progress", "Core Module Implementation", "Implement MemoryManager")
    csm.add_insight("Realized structured memories are key for LLM context.")
    
    print("\nUpdated State for Prompt:")
    print(csm.get_formatted_state_for_prompt())
    # csm.save_state() # update_state_variable now auto-saves
