# Dev Brain

A "Dev Brain" for your codebase: a governance-aware, probabilistic knowledge vault that acts as a guardian for your architecture.

## Overview

This project implements a system that:
1.  **Observes** code changes (Guardian).
2.  **Updates** a probabilistic model of rule compliance (Quantum State).
3.  **Generates** governance-aware prompts for Coding LLMs (Composer).

It ensures that AI coding assistants respect architectural rules ("decisions") by injecting relevant context and constraints into their prompts.

## Features

-   **JSON Vault**: Stores knowledge in `.dev_brain/` (summaries, decisions, rule states, frames, graph).
-   **Guardian**: Analyzes user requests and code changes to update compliance beliefs.
-   **Composer**: Generates prompts with "Context Lensing" and "Governance State".
-   **Pipeline**: Orchestrates the flow from Change Event -> Guardian -> Composer.
-   **HTTP API**: Exposes the pipeline as a service.
-   **OpenAI/Codex Integration**: Uses OpenAI models (default: `gpt-5.1`) for file summarization and automated coding.
-   **VS Code Extension**: "Dev Brain Companion" to trigger the pipeline directly from your editor.

## Installation

Requires Python 3.10+ and Node.js (for the VS Code extension).

1.  Clone the repository.
2.  Install Python dependencies:
    ```bash
    pip install pydantic fastapi uvicorn openai
    ```
3.  Set Environment Variables:
    ```powershell
    $env:QDB_CODEX_API_KEY="your-openai-api-key"
    # Optional:
    # $env:QDB_CODEX_MODEL="gpt-5.1"
    # $env:QDB_CODER_MODEL="gpt-5.1"
    ```

## Usage

### 1. Start the Server
The core backend must be running for the API and VS Code extension to work.
```bash
python -m dev_brain.cli_server
```
The API will be available at `http://127.0.0.1:8000`.

### 2. VS Code Extension
The **Dev Brain Companion** allows you to run the cycle from VS Code.

1.  Navigate to `dev-brain-vscode/`.
2.  Install dependencies: `npm install`.
3.  Compile: `npm run compile`.
4.  Run/Debug: Open the folder in VS Code and press `F5`.
5.  Command: `Dev Brain: Run Cycle for Current File`.

### 3. CLI Demos

#### Full Pipeline Demo
Runs the end-to-end flow: User Request -> Guardian (Update Vault) -> Composer (Generate Prompt).
```bash
python -m dev_brain.demo_full
```

#### Coder Agent Demo
Demonstrates the full loop including an automated call to the Coder LLM (OpenAI).
```bash
python -m dev_brain.demo_coder
```

#### Codex Ingestion
Batch processes files to generate summaries using OpenAI.
```bash
python -m dev_brain.codex_ingest
```

## Project Structure

-   `dev_brain/`: Main Python package.
    -   `models.py`: Pydantic models for the vault.
    -   `vault_io.py`: JSON read/write operations.
    -   `governance.py`: Logic for selecting relevant rules.
    -   `metrics.py`: Heuristics for belief updates.
    -   `guardian.py`: Core logic for processing changes.
    -   `composer.py`: Prompt generation logic.
    -   `pipeline.py`: Orchestration.
    -   `server.py`: FastAPI application.
    -   `openai_client.py`: Shared OpenAI client wrapper.
    -   `codex_brain.py`: File summarization logic.
    -   `coder_agent.py`: Automated coding agent logic.
-   `dev-brain-vscode/`: VS Code extension source.
-   `.dev_brain/`: The Knowledge Vault (JSON files).
-   `tests/`: Unit tests.

## Testing

Run the unit tests:
```bash
python -m unittest tests/test_dev_brain.py
```
