# Dev Brain Companion

VS Code extension for the Dev Brain system.

## Requirements

- Node.js and npm installed.
- Python QDB backend running.

## Setup

1.  **Start the QDB Server**:
    ```bash
    python -m dev_brain.cli_server
    ```

2.  **Install Dependencies**:
    ```bash
    cd dev-brain-vscode
    npm install
    ```

3.  **Build**:
    ```bash
    npm run compile
    ```

## Debugging

1.  Open the `dev-brain-vscode` folder in VS Code.
2.  Press `F5` to launch the **Extension Development Host**.

## Usage

1.  In the Extension Development Host window, open your project (the one with `.dev_brain`).
2.  Open a Python file you want to work on.
3.  Open the Command Palette (`Ctrl+Shift+P`).
4.  Run: `Dev Brain: Run Cycle for Current File`.
5.  Enter your request (e.g., "Add logging to this function").
6.  A new tab will open with the generated **Governance-Aware Prompt**.
7.  Copy this prompt to your Coder LLM (e.g., Claude Code).
