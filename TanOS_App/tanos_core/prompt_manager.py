# tanos_core/prompt_manager.py
from pathlib import Path
from typing import Dict, Optional

from . import settings

class PromptManager:
    """Manages loading and accessing TanOS module prompts."""
    def __init__(self, prompts_dir: Path = Path(settings.TANOS_PROMPTS_DIR)):
        self.prompts_dir = prompts_dir
        self.prompt_cache: Dict[str, str] = {}

    def _get_prompt_filepath(self, module_key: str, prompt_filename: str) -> Path:
        # module_key corresponds to directory names like 'CaptainsLog', 'ChartRoom'
        return self.prompts_dir / module_key / prompt_filename

    def load_prompt(self, module_key: str, prompt_filename: str, force_reload: bool = False) -> Optional[str]:
        """Loads a specific prompt file content."""
        cache_key = f"{module_key}/{prompt_filename}"
        if not force_reload and cache_key in self.prompt_cache:
            return self.prompt_cache[cache_key]

        filepath = self._get_prompt_filepath(module_key, prompt_filename)
        if not filepath.exists():
            print(f"Warning: Prompt file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.prompt_cache[cache_key] = content
            print(f"Loaded prompt: {cache_key}")
            return content
        except Exception as e:
            print(f"Error loading prompt {filepath}: {e}")
            return None

    def get_workshop_conceptual_tool_prompt(self, tool_filename: str) -> Optional[str]:
        """Helper to load conceptual tools from the Workshop/Tools/ directory."""
        return self.load_prompt("Workshop", f"Tools/{tool_filename}")

if __name__ == '__main__':
    pm = PromptManager()
    captains_log_prompt = pm.load_prompt("CaptainsLog", "Nomad_Core_Persona_and_State.txt")
    if captains_log_prompt:
        print(f"\nSuccessfully loaded Captain's Log prompt (first 100 chars): {captains_log_prompt[:100]}...")

    systems_thinking_tool = pm.get_workshop_conceptual_tool_prompt("apply_systems_thinking_lens_prompt.txt")
    if systems_thinking_tool:
        print(f"\nSuccessfully loaded Systems Thinking Tool prompt (first 100 chars): {systems_thinking_tool[:100]}...")
