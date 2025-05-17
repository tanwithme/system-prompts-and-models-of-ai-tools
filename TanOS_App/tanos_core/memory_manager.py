# tanos_core/memory_manager.py
import json
import yaml # Requires PyYAML
from pathlib import Path
from typing import Dict, Any, Optional, List

from . import settings

class MemoryManager:
    """
    Manages loading, accessing, and suggesting updates to Tan's MEMORIES.
    Assumes memories are stored as structured JSON or YAML files.
    Markdown versions are the source of truth, this class would work with
    converted/structured representations.
    """
    def __init__(self, memories_dir: Path = settings.MEMORIES_DIR):
        self.memories_dir = memories_dir
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self._ensure_memory_files_exist()

    def _ensure_memory_files_exist(self):
        """
        Creates empty JSON files if they don't exist, for core memories.
        In a real setup, a script would convert MD to these structured formats.
        """
        core_memory_keys = [
            "tan_core_identity_values",
            "tan_growth_plan_goals",
            "tan_cognitive_os_preferences"
        ]
        for key in core_memory_keys:
            file_path = self.memories_dir / f"{key}.json" # Assuming JSON for structure
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump({"placeholder_data": f"Data for {key} to be populated from Markdown." , "version": "1.0", "last_reviewed_by_tan": None}, f, indent=4)
                print(f"Created placeholder memory file: {file_path}")


    def _get_memory_filepath(self, memory_key: str) -> Path:
        # Add logic to map memory_key to actual filenames (e.g., .json, .yaml)
        # For now, assuming key is part of filename and it's JSON
        filename = f"{memory_key}.json"
        return self.memories_dir / filename

    def load_memory(self, memory_key: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """Loads a specific memory file (e.g., 'tan_core_identity') into cache."""
        if not force_reload and memory_key in self.memory_cache:
            return self.memory_cache[memory_key]

        filepath = self._get_memory_filepath(memory_key)
        if not filepath.exists():
            print(f"Warning: Memory file not found for key '{memory_key}' at {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Detect if YAML or JSON based on extension, or try both
                if filepath.suffix == ".yaml" or filepath.suffix == ".yml":
                    data = yaml.safe_load(f)
                elif filepath.suffix == ".json":
                    data = json.load(f)
                else: # Default to trying JSON, then YAML for unknown extensions
                    try:
                        f.seek(0)
                        data = json.load(f)
                    except json.JSONDecodeError:
                        f.seek(0)
                        data = yaml.safe_load(f)
                
                self.memory_cache[memory_key] = data
                print(f"Loaded memory: {memory_key}")
                return data
        except Exception as e:
            print(f"Error loading memory '{memory_key}' from {filepath}: {e}")
            return None

    def get_memory_section(self, memory_key: str, section_path: Optional[List[str]] = None) -> Any:
        """
        Retrieves a specific section from a loaded memory using a path of keys.
        Example: get_memory_section('tan_core_identity', ['Core Values', 'Freedom'])
        """
        memory_data = self.load_memory(memory_key)
        if memory_data is None:
            return None

        if not section_path:
            return memory_data # Return whole memory if no section specified

        current_level = memory_data
        try:
            for key_part in section_path:
                current_level = current_level[key_part]
            return current_level
        except (KeyError, TypeError):
            print(f"Warning: Section path '{'/'.join(section_path)}' not found in memory '{memory_key}'.")
            return None

    def get_full_memory_content_for_prompt(self, memory_key: str) -> str:
        """
        Returns the full content of a memory, formatted as a string suitable for an LLM prompt.
        This might involve loading the original Markdown or pretty-printing the structured data.
        For now, it will pretty-print the JSON/YAML.
        """
        memory_data = self.load_memory(memory_key)
        if memory_data:
            # Pretty print JSON/YAML for inclusion in prompt
            return json.dumps(memory_data, indent=2)
        return f"[Memory content for '{memory_key}' could not be loaded or is empty]"

    def suggest_memory_update(self, memory_key: str, suggested_change_description: str, section_path: Optional[List[str]] = None) -> None:
        """
        Logs a suggestion for Tan to manually update a memory file.
        In a real app, this might create a pending change request for Tan to review.
        """
        # This is a conceptual logging. Actual update is manual by Tan.
        print(f"\n--- MEMORY UPDATE SUGGESTION for Tan ---")
        print(f"Memory File Key: {memory_key} (Likely maps to {self._get_memory_filepath(memory_key).name})")
        if section_path:
            print(f"Target Section: {' -> '.join(section_path)}")
        print(f"Suggested Change: {suggested_change_description}")
        print(f"Action: Tan, please review and manually update the corresponding Markdown/structured memory file if you agree.")
        print(f"---------------------------------------\n")
        # Potentially log this suggestion to a dedicated file or the Nomad Changelog via ChangelogManager

if __name__ == '__main__':
    mm = MemoryManager()
    # Example: Convert your MD files to JSON in tanos_data/memories/ first
    # For example, tanos_data/memories/tan_core_identity_values.json
    # Then test loading:
    core_id = mm.load_memory("tan_core_identity_values")
    if core_id:
        print("\nSuccessfully loaded tan_core_identity_values:")
        # print(json.dumps(core_id, indent=2))
        print(f"Version: {mm.get_memory_section('tan_core_identity_values', ['version'])}")
        print(f"Core Value (Freedom): {mm.get_memory_section('tan_core_identity_values', ['Prevailing Winds (Core Values)', 0])}") # Assuming list
    
    mm.suggest_memory_update(
        "tan_cognitive_os_preferences",
        "Consider adding a new 'Preferred Communication Channels' section under 'Communication & Writing Style Preferences'.",
        ["Communication & Writing Style Preferences"]
    )
    # print(mm.get_full_memory_content_for_prompt("tan_growth_plan_goals"))
