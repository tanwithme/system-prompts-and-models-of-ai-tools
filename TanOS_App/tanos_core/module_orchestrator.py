# tanos_core/module_orchestrator.py
from typing import Dict, Any, Optional

from .prompt_manager import PromptManager
from .state_manager import CaptainsLogStateManager
from .llm_interface import LLMInterface
from .memory_manager import MemoryManager
from .changelog_manager import NomadChangelogManager
from . import settings  # For current date, time if needed directly

class TanOSModuleOrchestrator:
    """
    Orchestrates the activation of TanOS modules and manages the interaction flow.
    This is the core logic that simulates Nomad's "thinking" process based on
    the inter-module communication protocols defined in the prompts.
    """

    def __init__(self):
        self.prompt_manager = PromptManager()
        self.state_manager = CaptainsLogStateManager()
        self.llm_interface = LLMInterface()  # Uses LLM_PROVIDER from settings
        self.memory_manager = MemoryManager()
        self.changelog_manager = NomadChangelogManager()
        print("TanOS Module Orchestrator initialized.")

    def _get_full_context_for_llm(self, active_module_key: Optional[str] = None) -> str:
        """
        Compiles the full context string to be sent to the LLM.
        Includes Captain's Log state and relevant MEMORIES.
        Can be tailored if a specific module needs specific memory types.
        """
        captains_log_state_str = self.state_manager.get_formatted_state_for_prompt()

        # Smartly load relevant memories based on active module or general context
        # For now, let's load all core memories for general context.
        # A more advanced version could selectively load based on module/query.
        core_identity_mem = self.memory_manager.get_full_memory_content_for_prompt("tan_core_identity_values")
        growth_plan_mem = self.memory_manager.get_full_memory_content_for_prompt("tan_growth_plan_goals")
        cognitive_os_mem = self.memory_manager.get_full_memory_content_for_prompt("tan_cognitive_os_preferences")

        # Update Nomad version in state from changelog
        latest_nomad_version = self.changelog_manager.get_latest_version()
        if latest_nomad_version:
            self.state_manager.update_nomad_version(latest_nomad_version)  # This also saves state

        full_context = (
            f"--- CURRENT CAPTAIN'S LOG OPERATIONAL STATE ---\n"
            f"{captains_log_state_str}\n"
            f"--- END CAPTAIN'S LOG ---\n\n"
            f"--- RELEVANT MEMORIES (Tan's Core Profile) ---\n"
            f"**Core Identity & Values Summary (from MEMORIES/tan_core_identity_values.md - structured as {settings.MEMORIES_DIR / 'tan_core_identity_values.json'})**\n"
            f"{core_identity_mem}\n\n"
            f"**Growth Plan & Goals Summary (from MEMORIES/tan_growth_plan_goals.md - structured as {settings.MEMORIES_DIR / 'tan_growth_plan_goals.json'})**\n"
            f"{growth_plan_mem}\n\n"
            f"**Cognitive & OS Preferences Summary (from MEMORIES/tan_cognitive_os_preferences.md - structured as {settings.MEMORIES_DIR / 'tan_cognitive_os_preferences.json'})**\n"
            f"{cognitive_os_mem}\n"
            f"--- END MEMORIES ---\n"
        )
        return full_context

    def process_user_interaction(self, user_input: str, active_module_key: str) -> str:
        """
        Processes user input through a specified TanOS module.
        This is the main interaction loop simulation.
        """
        print(f"\n>>> Orchestrator: Processing input for Module: {active_module_key} <<<")
        print(f"User Input: {user_input}")

        # 1. Load the System Prompt for the active module
        # Module key mapping to prompt files (could be more dynamic)
        prompt_file_map = {
            "CaptainsLog": "Nomad_Core_Persona_and_State.txt",
            "ChartRoom": "Planning_Module_Prompt.txt",
            "Workshop": "Execution_Module_Prompt.txt",
            "PhilosophersPorch": "Reflection_Module_Prompt.txt",
            "CrowsNest": "Sensory_Input_Module_Prompt.txt",
        }
        system_prompt_filename = prompt_file_map.get(active_module_key)
        if not system_prompt_filename:
            return f"[Orchestrator Error: Unknown module key '{active_module_key}']"

        system_prompt = self.prompt_manager.load_prompt(active_module_key, system_prompt_filename)
        if not system_prompt:
            return f"[Orchestrator Error: Could not load prompt for {active_module_key}/{system_prompt_filename}]"

        # 2. Compile Full Context for LLM
        full_llm_context = self._get_full_context_for_llm(active_module_key)

        # 3. Send to LLM
        llm_response_text = self.llm_interface.send_prompt(
            system_prompt=system_prompt,
            user_prompt=user_input,
            full_context_str=full_llm_context,
        )

        # 4. Post-LLM Processing (Conceptual - based on Inter-Module Protocols)
        # This is where the logic from the "VI. Inter-Module Communication Protocols"
        # section of each module prompt would be implemented.
        # For a skeleton, we just print the response and a note about next steps.

        print(f"Raw LLM Response for {active_module_key} (first 150 chars): {llm_response_text[:150]}...")

        # Example conceptual post-processing:
        if active_module_key == "CrowsNest":
            # Crow's Nest might update CaptainsLog state directly after parsing LLM response
            # For example, if LLM helps structure Tan's input into loggable data:
            # self.state_manager.update_state_variable("tan_mood_energy_summary", "Updated by CrowsNest")
            # self.state_manager.update_state_variable("health_metric_flags", "HRV Yellow (Example)")
            print(
                f"[Orchestrator Note: {active_module_key} would now parse LLM response to update Captain's Log state (mood, flags) and possibly trigger other modules if thresholds are met.]"
            )

        elif active_module_key == "ChartRoom":
            # ChartRoom might update active projects in CaptainsLog
            # and pass tasks to Workshop
            print(
                f"[Orchestrator Note: {active_module_key} would parse LLM response for plans/tasks, update Captain's Log projects, and conceptually pass tasks to Workshop.]"
            )
            # self.state_manager.add_active_project("New Project from ChartRoom", "Planned", "Phase 1", "Research Topic X")

        elif active_module_key == "Workshop":
            # Workshop executes tasks, its outcomes update ChartRoom (via conceptual logging)
            print(
                f"[Orchestrator Note: {active_module_key} simulated tool use. Outcome logged. ChartRoom needs this outcome to determine next step.]"
            )

        elif active_module_key == "PhilosophersPorch":
            # Philosopher's Porch generates insights and changelog drafts
            print(
                f"[Orchestrator Note: {active_module_key} session completed. Tan to review insights for manual MEMORIES/Prompt updates and `Nomad_Changelog.md` commit.]"
            )
            # Example: self.changelog_manager.add_entry(...) based on LLM's drafted entry.
            # Example: self.memory_manager.suggest_memory_update(...)
            # self.state_manager.add_insight("Reflection on X completed.")

        # This is crucial: Save state after any conceptual updates
        self.state_manager.save_state()

        return llm_response_text  # Return the direct LLM response for now

    def simulate_conceptual_tool(self, conceptual_tool_filename: str, initial_tan_input: str) -> str:
        """Simulates guiding Tan through a conceptual tool."""
        print(f"\n>>> Orchestrator: Simulating Conceptual Tool: {conceptual_tool_filename} <<<")
        print(f"Initial Input from Tan: {initial_tan_input}")

        tool_system_prompt = self.prompt_manager.get_workshop_conceptual_tool_prompt(conceptual_tool_filename)
        if not tool_system_prompt:
            return f"[Orchestrator Error: Could not load conceptual tool prompt: {conceptual_tool_filename}]"

        full_llm_context = self._get_full_context_for_llm("Workshop")  # Context for workshop generally

        # The LLM will now embody this tool's prompt and guide Tan
        # The "user_prompt" here is Tan's initial engagement with the tool
        llm_response_text = self.llm_interface.send_prompt(
            system_prompt=tool_system_prompt,  # The tool's own multi-step guidance prompt
            user_prompt=f"(Now guiding Tan through the '{conceptual_tool_filename}' process. Initial context/question from Tan: '{initial_tan_input}')\nLet's begin with the first step of this conceptual tool.",
            full_context_str=full_llm_context,
        )

        # The conversation would continue, with Tan responding to the tool's guided questions
        # The final step of each conceptual tool asks Tan to summarize.
        # That summary would then be logged.
        print(
            f"[Orchestrator Note: Conceptual tool '{conceptual_tool_filename}' initiated. LLM will guide Tan. Tan will provide a summary at the end as per tool's prompt.]"
        )
        return llm_response_text  # Return the LLM's first guiding message for the tool


if __name__ == "__main__":
    orchestrator = TanOSModuleOrchestrator()

    print("\n--- Simulating CrowsNest Interaction ---")
    # Tan provides input as if responding to CrowsNest's morning prompt
    tan_crowsnest_input = "Sleep 7/10, 7.5hrs. HRV 52, RHR 58. AM Supps Yes. Mood Spring Neutral, Energy 6."
    crowsnest_response = orchestrator.process_user_interaction(tan_crowsnest_input, "CrowsNest")
    # print(f"\nNomad (CrowsNest) Says:\n{crowsnest_response}")  # Full response is long due to mock

    print("\n--- Simulating ChartRoom Interaction ---")
    tan_chartroom_input = "I want to start a new project: 'Learn Advanced Python'."
    chartroom_response = orchestrator.process_user_interaction(tan_chartroom_input, "ChartRoom")
    # print(f"\nNomad (ChartRoom) Says:\n{chartroom_response}")

    print("\n--- Simulating Workshop - Conceptual Tool ---")
    tan_workshop_tool_input = "Let's use Systems Thinking for my 'Learn Advanced Python' project to understand bottlenecks."
    # The module_orchestrator.process_user_interaction for "Workshop" would typically get a task from ChartRoom like
    # "Guide Tan through apply_systems_thinking_lens_prompt.txt for 'Learn Advanced Python'"
    # For this test, we call simulate_conceptual_tool directly
    workshop_tool_response = orchestrator.simulate_conceptual_tool(
        "apply_systems_thinking_lens_prompt.txt",
        tan_workshop_tool_input,
    )
    # print(f"\nNomad (Workshop - Systems Thinking Tool) Says:\n{workshop_tool_response}")
