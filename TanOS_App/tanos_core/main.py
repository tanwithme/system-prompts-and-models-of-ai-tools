# tanos_core/main.py
import click  # Requires click library: pip install click
import json
from typing import Optional
from datetime import datetime

from .module_orchestrator import TanOSModuleOrchestrator
from .state_manager import CaptainsLogStateManager
from .memory_manager import MemoryManager
from .changelog_manager import NomadChangelogManager
from .architectos_engine import ArchitectOSEngine
from . import settings

orchestrator = TanOSModuleOrchestrator()
state_manager = orchestrator.state_manager
memory_manager = orchestrator.memory_manager
changelog_manager = orchestrator.changelog_manager
architect_engine = ArchitectOSEngine(orchestrator.prompt_manager, orchestrator.llm_interface, orchestrator.memory_manager)

@click.group()
def cli():
    """TanOS App: Your Personalized AI Copilot and Operating System."""
    pass

@cli.command(name="interact")
@click.option('--module', required=True,
              type=click.Choice(['CaptainsLog', 'ChartRoom', 'Workshop', 'PhilosophersPorch', 'CrowsNest'], case_sensitive=False),
              help="The TanOS module to interact with.")
@click.option('--input', 'user_input', required=True, prompt="Your input for Nomad", help="Your query or input for the selected module.")
def interact_with_module(module: str, user_input: str):
    """Interact with a specific TanOS module (Nomad)."""
    click.echo(f"Engaging Nomad ({module})...")
    response = orchestrator.process_user_interaction(user_input, module)
    click.echo("\n--- Nomad's Response ---")
    click.echo(response)
    click.echo("----------------------")

@cli.command(name="log-health")
@click.option('--sleep-quality', type=click.FLOAT, help="Sleep quality (1-10)")
@click.option('--sleep-hours', type=click.FLOAT, help="Hours slept")
@click.option('--hrv', type=click.INT, help="Morning HRV")
@click.option('--rhr', type=click.INT, help="Morning RHR")
@click.option('--am-supps', type=click.Choice(['yes', 'no', 'partial'], case_sensitive=False), help="AM Supplements taken?")
@click.option('--pm-supps', type=click.Choice(['yes', 'no', 'partial'], case_sensitive=False), help="PM Supplements taken?")
@click.option('--diet-track', type=click.Choice(['on', 'partial', 'off'], case_sensitive=False), help="No-carb/High-protein diet status")
@click.option('--tretinoin', type=click.Choice(['yes', 'no'], case_sensitive=False), help="Tretinoin applied?")
@click.option('--mood', help="Current mood (e.g., Spring expansive, Neutral, Stressed)")
@click.option('--energy', type=click.INT, help="Energy level (1-10)")
@click.option('--stress', type=click.INT, help="Stress level (1-10)")
def log_health_data(**kwargs):
    """Log health and subjective state data for CrowsNest."""
    click.echo("Health Data to Log for CrowsNest:")
    log_input_parts = []
    for key, value in kwargs.items():
        if value is not None:
            click.echo(f"- {key.replace('_', ' ').title()}: {value}")
            log_input_parts.append(f"{key.replace('_', ' ').title()}: {value}")

    if not log_input_parts:
        click.echo("No health data provided to log.")
        return

    crowsnest_input_str = "; ".join(log_input_parts)
    click.echo(f"\nLogging health metrics: '{crowsnest_input_str}'")

    response = orchestrator.log_health_metrics(kwargs)
    click.echo("\n--- Nomad (CrowsNest) Response ---")
    click.echo(response)
    click.echo("--------------------------------")
    click.echo("Captain's Log updated with these health metrics.")

@cli.command(name="view-state")
def view_captains_log_state():
    """View the current Captain's Log operational state."""
    state = state_manager.get_formatted_state_for_prompt()
    click.echo("--- Current Captain's Log State ---")
    click.echo(state)
    click.echo("---------------------------------")

@cli.command(name="view-memory")
@click.argument('memory_key', type=click.Choice(['tan_core_identity_values', 'tan_growth_plan_goals', 'tan_cognitive_os_preferences'], case_sensitive=False))
def view_memory_file(memory_key: str):
    """View the content of a structured MEMORIES file."""
    content = memory_manager.get_full_memory_content_for_prompt(memory_key)
    click.echo(f"--- Content of MEMORY: {memory_key} ---")
    click.echo(content if content else "Memory not found or empty.")
    click.echo("------------------------------------")

@cli.command(name="view-changelog")
@click.option('--limit', default=5, type=click.INT, help="Number of recent entries to show.")
def view_nomad_changelog(limit: int):
    """View recent entries from Nomad's conceptual changelog."""
    entries = changelog_manager.get_changelog_entries(limit)
    click.echo(f"--- Nomad Changelog (Last {limit} Entries) ---")
    if not entries:
        click.echo("Changelog is empty.")
    for entry in entries:
        click.echo(f"Version: {entry.get('version')} (Date: {entry.get('date')})")
        click.echo(f"  Summary: {entry.get('summary')}")
        click.echo(f"  Impacted: {', '.join(entry.get('impacted_modules', []))}")
        click.echo(f"  Files Updated by Tan: {', '.join(entry.get('files_updated_by_tan', []))}")
        click.echo("-" * 20)
    click.echo("---------------------------------------")

@cli.command(name="evolve-prompt")
@click.option('--module', 'module_key', required=True,
              type=click.Choice(['CaptainsLog', 'ChartRoom', 'Workshop', 'PhilosophersPorch', 'CrowsNest'], case_sensitive=False),
              help="The TanOS module whose prompt you want to evolve.")
@click.option('--file', 'prompt_filename', required=True, help="The filename of the prompt within the module (e.g., 'Planning_Module_Prompt.txt').")
@click.option('--objective', required=True, help="A clear description of the improvement objective for this prompt.")
def evolve_prompt_command(module_key: str, prompt_filename: str, objective: str):
    """Engage ArchitectOS to evolve a specific TanOS prompt."""
    click.echo(f"Engaging ArchitectOS to evolve: {module_key}/{prompt_filename}")
    click.echo(f"Objective: {objective}")

    results = architect_engine.run_gcm_cycle(
        objective_space_description=objective,
        current_target_prompt_key=(module_key, prompt_filename),
    )

    click.echo("\n--- ArchitectOS G-C-M Cycle Output ---")
    click.echo("Suggested Evolved Prompt Text/Concepts:")
    click.echo(results.get("evolved_prompt_suggestions_text", "No evolved suggestions generated."))
    click.echo("\nGenerator Proposals Text:")
    click.echo(results.get("generator_proposals_text", "N/A"))
    click.echo("\nCritic Notes Text:")
    click.echo(results.get("critic_notes_text", "N/A"))
    click.echo(f"\nSuggested Next Architect Cycle: {results.get('suggested_next_architect_cycle', 'Review and implement.')}")
    click.echo("------------------------------------")
    click.echo("ACTION: Review the 'evolved_prompt_suggestions_text'. If a suggestion is valuable,")
    click.echo(f"manually update the '{settings.TANOS_PROMPTS_DIR}/{module_key}/{prompt_filename}' file.")
    click.echo("Then, draft and add an entry to Nomad's Changelog using 'tanos add-changelog-entry'.")

@cli.command(name="add-changelog-entry")
@click.option('--version', required=True, help="New version string (e.g., 0.3.1)")
@click.option('--summary', required=True, help="Summary of the learning/refinement.")
@click.option('--impacted', required=True, help="Comma-separated list of impacted modules (e.g., ChartRoom,Workshop).")
@click.option('--files-updated', required=True, help="Comma-separated list of actual files Tan updated (e.g., ChartRoom/Planning_Module_Prompt.txt).")
def add_changelog_entry_command(version: str, summary: str, impacted: str, files_updated: str):
    """Manually add an entry to Nomad's Changelog after updating prompts."""
    impacted_list = [m.strip() for m in impacted.split(',')]
    files_list = [f.strip() for f in files_updated.split(',')]
    date_str = datetime.now().strftime("%Y-%m-%d")

    changelog_manager.add_entry(
        version=version,
        date=date_str,
        summary=summary,
        impacted_modules=impacted_list,
        files_updated_by_tan=files_list,
    )
    click.echo(f"Entry for version {version} added to Nomad changelog.")
    state_manager.update_nomad_version(version)
    click.echo(f"Captain's Log nomad_version updated to {version}.")

if __name__ == '__main__':
    cli()
# To run from project root: python -m tanos_core.main [COMMAND] [OPTIONS]
# Example: python -m tanos_core.main interact --module ChartRoom --input "Help me plan a new blog post"
# Example: python -m tanos_core.main log-health --sleep-quality 8 --sleep-hours 7 --mood "Spring expansive"
# Example: python -m tanos_core.main view-state
# Example: python -m tanos_core.main evolve-prompt --module ChartRoom --file Planning_Module_Prompt.txt --objective "Improve handling of vague goals"
