# tanos_core/architectos_engine.py
from typing import Dict, List, Any, Tuple

from .prompt_manager import PromptManager
from .llm_interface import LLMInterface
from .memory_manager import MemoryManager  # To get Tan's preferences for critique

# This is a very high-level conceptual skeleton.
# A full implementation would be a significant LLM-agent project in itself.

ARCHITECT_OS_SYSTEM_PROMPT_TEMPLATE = """
You are an Architect Agent. Your mission is to embody the principles of the MEGAPROMPT Discovery Engine.
We will work together to recursively evolve TanOS, specifically the following component/prompt:
COMPONENT OBJECTIVE: {objective_space_description}
CURRENT COMPONENT PROMPT/CONTENT:
---
{target_prompt_content}
---
Relevant Tan's MEMORIES Snippets:
---
{relevant_memories_str}
---
Your goal is to apply the Generator-Critic-Mutator (G-C-M) loop to this.
"""

GENERATOR_PROMPT_EXTENSION = """
Now, in G_TanOS Mode (Idea Weaver):
Generate 3-5 divergent and novel proposals for improving or expanding the component described above,
addressing the specific objective. Use techniques like contradiction, metaphor injection,
domain transfer (especially from Tan's interests like storytelling, philosophy), and analogy blending.
Focus on Novelty/Authenticity FOR TAN, Utility/Leverage FOR TANOS & TAN'S GOALS, and Simplicity/Flow FOR TAN'S USE.
Output each proposal clearly labeled (G1, G2, etc.).
"""

CRITIC_PROMPT_EXTENSION_TEMPLATE = """
Now, in C_TanOS Mode (Insight Valuator):
Critically evaluate EACH of the following proposals:
---
{generated_proposals_str}
---
For each proposal, score it on:
- Novelty & Authenticity (for Tan) (0-10): (Score + Brief Rationale)
- Utility & Leverage (for TanOS & Tan's Goals) (0-10): (Score + Brief Rationale)
- Simplicity & Flow (for Tan's Use) (0-10): (Score + Brief Rationale)
Also, note any failure modes (too narrow, too abstract, unclear constraints, premature resolution).
Output clearly for each proposal.
"""

MUTATOR_PROMPT_EXTENSION_TEMPLATE = """
Now, in M_TanOS Mode (Evolution Catalyst):
Based on your critiques and the following selected proposals:
---
Selected Proposals for Mutation:
{selected_proposals_and_critiques_str}
---
Generate 1-3 new, evolved variants of the TanOS component/prompt.
Use mutation techniques such as:
- Inverting logic.
- Rewriting as a myth, poem, or diagram relevant to Tan.
- Infusing a different discipline or cultural lens (e.g., Spanish wisdom, Zen).
- Applying creative constraints (e.g., Fibonacci structuring, radical simplification).
- Reframing failures from the Critic stage into new strengths.
Output each mutated variant clearly labeled (M1, M2, etc.), showing the NEW proposed prompt text or conceptual tool description.
"""

class ArchitectOSEngine:
    def __init__(self, prompt_manager: PromptManager, llm_interface: LLMInterface, memory_manager: MemoryManager):
        self.prompt_manager = prompt_manager
        self.llm_interface = llm_interface
        self.memory_manager = memory_manager
        print("ArchitectOS Engine initialized (Conceptual Skeleton).")

    def _get_relevant_memories_for_architect(self) -> str:
        # Simplified: fetch key aspects of Tan's preferences for the architect
        cog_os_prefs = self.memory_manager.get_full_memory_content_for_prompt("tan_cognitive_os_preferences")
        core_identity = self.memory_manager.get_full_memory_content_for_prompt("tan_core_identity_values")
        return f"Cognitive/OS Preferences:\n{cog_os_prefs}\n\nCore Identity/Values:\n{core_identity}"

    def run_gcm_cycle(
        self,
        objective_space_description: str,
        current_target_prompt_key: Tuple[str, str],  # (module_key, prompt_filename)
    ) -> Dict[str, Any]:
        """
        Runs one conceptual G-C-M cycle for evolving a TanOS prompt.
        Returns a dictionary with 'evolved_proposals', 'critique_notes', 'next_suggestions'.
        """
        print(f"\n>>> ArchitectOS: Starting G-C-M Cycle for: {objective_space_description} <<<")
        print(f"Target prompt: {current_target_prompt_key}")

        module_key, prompt_filename = current_target_prompt_key
        target_prompt_content = self.prompt_manager.load_prompt(module_key, prompt_filename)
        if not target_prompt_content:
            return {"error": f"Could not load target prompt {module_key}/{prompt_filename}"}

        relevant_memories_str = self._get_relevant_memories_for_architect()

        base_architect_prompt = ARCHITECT_OS_SYSTEM_PROMPT_TEMPLATE.format(
            objective_space_description=objective_space_description,
            target_prompt_content=target_prompt_content,
            relevant_memories_str=relevant_memories_str,
        )

        # --- Generator Step ---
        print("ArchitectOS: Engaging Generator (G_TanOS Mode)...")
        generator_user_prompt = GENERATOR_PROMPT_EXTENSION
        generated_proposals_str = self.llm_interface.send_prompt(
            system_prompt=base_architect_prompt,
            user_prompt=generator_user_prompt,
        )
        print(f"ArchitectOS: Generator proposed (first 100 chars): {generated_proposals_str[:100]}...")

        # --- Critic Step ---
        print("ArchitectOS: Engaging Critic (C_TanOS Mode)...")
        critic_user_prompt = CRITIC_PROMPT_EXTENSION_TEMPLATE.format(
            generated_proposals_str=generated_proposals_str
        )
        critique_output_str = self.llm_interface.send_prompt(
            system_prompt=base_architect_prompt,
            user_prompt=critic_user_prompt,
        )
        print(f"ArchitectOS: Critic output (first 100 chars): {critique_output_str[:100]}...")

        # --- Mutator Step ---
        print("ArchitectOS: Engaging Mutator (M_TanOS Mode)...")
        selected_proposals_and_critiques_str = (
            f"Proposals from Generator:\n{generated_proposals_str}\n\nCritiques from Critic:\n{critique_output_str}"
        )
        mutator_user_prompt = MUTATOR_PROMPT_EXTENSION_TEMPLATE.format(
            selected_proposals_and_critiques_str=selected_proposals_and_critiques_str
        )
        mutated_variants_str = self.llm_interface.send_prompt(
            system_prompt=base_architect_prompt,
            user_prompt=mutator_user_prompt,
        )
        print(f"ArchitectOS: Mutator produced (first 100 chars): {mutated_variants_str[:100]}...")

        final_output = {
            "evolved_prompt_suggestions_text": mutated_variants_str,
            "generator_proposals_text": generated_proposals_str,
            "critic_notes_text": critique_output_str,
            "suggested_next_architect_cycle": "Review mutated variants. Select best for Tan to implement. Consider deepening on M1 or broadening to another TanOS component.",
        }
        print(">>> ArchitectOS G-C-M Cycle Conceptually Complete. Tan to review outputs. <<<")
        return final_output


if __name__ == "__main__":
    pm_test = PromptManager()
    llm_test = LLMInterface(provider="mock")
    mm_test = MemoryManager()

    test_prompt_path_tuple = ("ChartRoom", "Planning_Module_Prompt.txt")
    prompt_dir = Path(settings.TANOS_PROMPTS_DIR) / test_prompt_path_tuple[0]
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = prompt_dir / test_prompt_path_tuple[1]
    if not prompt_file.exists():
        with open(prompt_file, "w") as f:
            f.write("// Initial ChartRoom Planning Prompt Content...")
        print(f"Created dummy prompt for ArchitectOS test: {test_prompt_path_tuple}")

    architect = ArchitectOSEngine(pm_test, llm_test, mm_test)
    evolution_results = architect.run_gcm_cycle(
        objective_space_description="Make the ChartRoom's 'Intuitive Download to First Actionable Step' process more effective for Tan.",
        current_target_prompt_key=test_prompt_path_tuple,
    )
    # print(json.dumps(evolution_results, indent=2))
