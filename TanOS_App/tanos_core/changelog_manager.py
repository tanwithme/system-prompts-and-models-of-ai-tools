# tanos_core/changelog_manager.py
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from . import settings

NOMAD_CHANGELOG_FILE = settings.CHANGELOGS_DIR / "nomad_changelog.json" # Store as structured data

class NomadChangelogManager:
    """Manages Nomad's conceptual changelog."""
    def __init__(self, changelog_file: Path = NOMAD_CHANGELOG_FILE):
        self.changelog_file = changelog_file
        self.changelog: List[Dict[str, Any]] = self._load_changelog()

    def _load_changelog(self) -> List[Dict[str, Any]]:
        if self.changelog_file.exists():
            try:
                with open(self.changelog_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Error decoding JSON from {self.changelog_file}. Initializing new changelog.")
            except Exception as e:
                print(f"Warning: Could not load changelog from {self.changelog_file} ({e}). Initializing new changelog.")
        return []

    def save_changelog(self) -> None:
        try:
            with open(self.changelog_file, 'w', encoding='utf-8') as f:
                json.dump(self.changelog, f, indent=4, ensure_ascii=False)
            print(f"Nomad changelog saved to {self.changelog_file}")
        except Exception as e:
            print(f"Error saving Nomad changelog to {self.changelog_file}: {e}")

    def add_entry(self, version: str, date: str, summary: str, impacted_modules: List[str], files_updated_by_tan: List[str]) -> None:
        new_entry = {
            "version": version,
            "date": date,
            "summary": summary,
            "impacted_modules": impacted_modules,
            "files_updated_by_tan": files_updated_by_tan,
            "timestamp": datetime.now().isoformat()
        }
        self.changelog.insert(0, new_entry) # Add to the beginning (most recent first)
        self.save_changelog()
        print(f"New entry added to Nomad changelog: Version {version}")

    def get_latest_version(self) -> Optional[str]:
        if not self.changelog:
            # Fallback to version in settings if changelog is empty
            # This part needs to align with how state_manager gets nomad_version
            # Or prompt manager could load the MD changelog for this
            # For now, let's return a default if empty
            return "0.3" # Default initial version
        return self.changelog[0].get("version")

    def get_changelog_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.changelog[:limit]

    def draft_changelog_entry_text(self, 
                                   current_version_str: str, 
                                   learning_summary: str, 
                                   affected_modules: List[str], 
                                   files_tan_will_update: List[str]
                                   ) -> str:
        """
        Helper to draft the text for a new changelog entry, for LLM to then confirm/use.
        Example: '**Version 0.3.1 (2025-05-16):** Learned: Tan prefers X for Y. Impacted: ChartRoom. Action: Tan updated ChartRoom prompt.'
        """
        try:
            major, minor, patch = map(int, current_version_str.split('.'))
            new_patch = patch + 1
            new_version_str = f"{major}.{minor}.{new_patch}"
        except ValueError:
            new_version_str = f"{current_version_str}-next" # Fallback if parsing fails
            print(f"Warning: Could not parse version '{current_version_str}' for increment. Using fallback.")

        date_str = datetime.now().strftime("%Y-%m-%d")
        
        entry_text = (
            f"**Version {new_version_str} ({date_str}):** "
            f"Learned/Refined: {learning_summary}. "
            f"Impacted Modules: {', '.join(affected_modules) if affected_modules else 'N/A'}. "
            f"Action: Tan updated {', '.join(files_tan_will_update) if files_tan_will_update else 'relevant prompts/memories'}."
        )
        return entry_text


if __name__ == '__main__':
    clm = NomadChangelogManager()
    print(f"\nInitial latest version from changelog: {clm.get_latest_version()}")

    # Example of Philosopher's Porch output guiding an update
    drafted_text_from_reflection = clm.draft_changelog_entry_text(
        current_version_str=clm.get_latest_version() or "0.3.0",
        learning_summary="Tan's 'good enough' clarity for new projects involves a 1-page outline.",
        affected_modules=["ChartRoom"],
        files_tan_will_update=["ChartRoom/Planning_Module_Prompt.txt"]
    )
    print(f"\nDrafted changelog entry text from reflection:\n{drafted_text_from_reflection}")

    # Tan reviews and confirms, then:
    # This assumes the new version string is extracted from the drafted_text or determined
    clm.add_entry(
        version="0.3.1", # This would be the new_version_str from above
        date=datetime.now().strftime("%Y-%m-%d"),
        summary="Tan's 'good enough' clarity for new projects involves a 1-page outline.",
        impacted_modules=["ChartRoom"],
        files_updated_by_tan=["ChartRoom/Planning_Module_Prompt.txt"]
    )
    print(f"\nUpdated latest version: {clm.get_latest_version()}")
    # print("\nRecent Changelog Entries:")
    # for entry in clm.get_changelog_entries(2):
    #     print(json.dumps(entry, indent=2))
