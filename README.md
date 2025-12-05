# Dev Brain

**Dev Brain** is a "Governance-Aware" knowledge vault for your codebase. It acts as a guardian for your software architecture, ensuring that AI coding assistants (like GitHub Copilot, Cursor, or custom agents) respect your project's rules and patterns.

## Why Dev Brain?

AI coding tools are powerful but often lack **architectural context**. They might generate code that works but violates your internal standards (e.g., "No direct SQL in service layers", "Always use the `Result` pattern").

Dev Brain solves this by:
1.  **Observing** your codebase and user requests.
2.  **Maintaining** a probabilistic model of rule compliance (the "Quantum State").
3.  **Injecting** relevant governance rules and context into the prompts sent to your coding LLM.

## Architecture

The system consists of three main components:

### 1. The Vault (`.dev_brain/`)
A local JSON-based knowledge graph that stores:
-   **Decisions**: Architectural rules and their status (e.g., `strict`, `lenient`).
-   **File Summaries**: AI-generated summaries of your code files (Interface, Logic, Data views).
-   **Rule States**: Probabilistic beliefs about how well each file complies with each rule.
-   **Frames**: A timeline of events (user requests, code changes) that evolves the brain's understanding.

### 2. The Guardian
A background process that analyzes changes. When you modify a file, the Guardian:
-   Checks for potential rule violations.
-   Updates the "compliance score" for relevant rules.
-   Records the event in the Vault's graph.

### 3. The Composer
The interface to your AI coder. When you ask for code, the Composer:
-   Retrieves the relevant file summaries.
-   Selects the most critical governance rules based on the current context.
-   Constructs a **Governance-Aware Prompt** that guides the LLM to write compliant code.

## Installation

### Prerequisites
-   **Python 3.10+**
-   **Node.js** (for VS Code extension packaging)
-   **OpenAI API Key** (for the backend brain)

### 1. Backend Setup
1.  Clone this repository.
2.  Install Python dependencies:
    ```bash
    pip install pydantic fastapi uvicorn openai
    ```
3.  Set your OpenAI API key:
    ```powershell
    $env:QDB_CODEX_API_KEY="sk-..."
    ```

### 2. VS Code Extension Setup
The **Dev Brain Companion** extension allows you to interact with the brain directly from VS Code.

1.  Navigate to the extension folder:
    ```bash
    cd dev-brain-vscode
    ```
2.  Install dependencies and package the extension:
    ```bash
    npm install
    npm install -g @vscode/vsce
    vsce package
    ```
3.  Install the generated `.vsix` file in VS Code:
    -   Go to the **Extensions** view (`Ctrl+Shift+X`).
    -   Click the `...` menu (Views and More Actions).
    -   Select **Install from VSIX...**.
    -   Choose the `dev-brain-vscode-0.0.1.vsix` file.

## Usage

### VS Code Extension ("Plug & Play")
Once installed, the extension automatically manages the backend server.

1.  Open your project folder in VS Code.
2.  Ensure you have a `.dev_brain` directory (or run `python -m dev_brain.codex_ingest` to initialize one).
3.  Open any code file.
4.  Open the Command Palette (`Ctrl+Shift+P`) and run:
    **`Dev Brain: Run Cycle for Current File`**
5.  Enter your request (e.g., *"Add a new method to calculate tax"*).
6.  The system will generate a prompt optimized for your architecture.

### Brain CLI
Inspect the state of your brain directly from the terminal.

-   **Global Status**:
    ```bash
    python -m dev_brain.brain_cli status
    ```
-   **List Rules**:
    ```bash
    python -m dev_brain.brain_cli rules
    ```
-   **File Governance State**:
    ```bash
    python -m dev_brain.brain_cli file path/to/file.py
    ```
-   **Recent Events (Frames)**:
    ```bash
    python -m dev_brain.brain_cli frames --last 5
    ```

## Configuration

You can configure the VS Code extension in your User/Workspace Settings:

-   `devBrain.pythonPath`: Path to the Python interpreter to use for the backend server (default: `python`).
-   `devBrain.serverUrl`: URL of the backend server if running manually (default: `http://127.0.0.1:8000`).

## Project Structure

-   `dev_brain/`: Core Python package (Guardian, Composer, Server).
-   `dev-brain-vscode/`: Source code for the VS Code extension.
-   `.dev_brain/`: The local vault storage (JSON files).
-   `tests/`: Unit tests.

## Testing

Run the full test suite to verify the system:
```bash
python -m unittest tests/test_dev_brain.py
python -m unittest tests/test_brain_cli.py
```
