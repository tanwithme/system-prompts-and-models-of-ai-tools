# TanOS Application - Version 0.1.0 (Skeletal)

Welcome to the TanOS Application codebase. This application is designed to be the runnable engine for Tan's personalized AI copilot and operating system, "Nomad," based on the TanOS promptware.

## Vision

TanOS aims to be a deeply personalized, locally-run software application that acts as Tan's cognitive co-pilot. Its core value is to make it effortless for Tan to interact with his own structured self-knowledge (`MEMORIES`) and refined operational prompts (`tanos_prompts`), augmented by LLM intelligence, to navigate life with greater clarity, purpose, and well-being.

## Current State

This is a **skeletal codebase (Version 0.1.0)**. It outlines the core architecture, modules, and intended functionality. It is **not yet runnable** as a full application and requires significant implementation of the logic within the defined classes and functions.

## Architecture

The application consists of:
- **`tanos_core/`**: The Python backend containing the main logic for managing memories, prompts, state, LLM interactions, and module orchestration.
- **`tanos_data/`**: Placeholder for local data storage (Memories, Captain's Log state, Changelog). These would ideally be structured files (JSON, YAML, SQLite).
- **`tanos_prompts/`**: A reference or copy of the TanOS promptware developed in Phase 3.
- **`tanos_frontend_cli/`**: The initial Command Line Interface for interacting with TanOS.
- **`tanos_frontend_web/`**: Placeholder for a future web-based UI.
- **`tests/`**: Placeholder for unit and integration tests.
- **`scripts/`**: Placeholder for utility scripts.

## Getting Started (Conceptual - For Future Development)

1.  **Set up Environment:**
    * Create a Python virtual environment.
    * Install dependencies: `pip install -r requirements.txt`
2.  **Configure `tanos_core/settings.py`:**
    * Set paths to your `MEMORIES` directory and `tanos_prompts` directory.
    * Configure LLM API keys or local model paths.
3.  **Initialize Data:**
    * Convert your Markdown `MEMORIES` files into the structured format expected by `MemoryManager` (e.g., JSON files in `tanos_data/memories/`).
    * Initialize `captains_log_state.json` and `nomad_changelog.json`.
4.  **Run the CLI:**
    * `python -m tanos_core.main --module ChartRoom --input "Plan my week"` (Example)

## Next Steps for Development

1.  Implement the core logic within each Python module in `tanos_core/`.
2.  Develop robust error handling and logging.
3.  Build out the CLI commands in `tanos_frontend_cli/commands.py`.
4.  Create comprehensive tests.
5.  Iteratively refine based on Tan's usage and feedback, using the `ArchitectOS` principles.
6.  Explore web UI development.

## Key Technologies (Suggested)

-   Python 3.10+
-   LLM: Local (Ollama, llama-cpp-python) or API-based (OpenAI, Anthropic)
-   Data Storage: JSON, YAML, or SQLite for local data.
-   CLI: `click` or `argparse` Python libraries.
-   Web UI (Future): Flask/Django + HTMX, or FastAPI + Svelte/Vue/React.
-   Containerization (Future): Docker.
