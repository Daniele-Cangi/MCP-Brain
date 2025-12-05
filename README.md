# Dev Brain

**Dev Brain** is a "Governance-Aware" knowledge vault for your codebase. It acts as a guardian for your software architecture, ensuring that AI coding assistants (like GitHub Copilot, Cursor, or custom agents) respect your project's rules and patterns.

## Quick Start (2 minutes)

1.  **Clone and Install Backend**:
    ```bash
    git clone <repo-url>
    cd dev-brain
    pip install -r requirements.txt
    ```

2.  **Initialize Vault**:
    This scans your code and creates the initial knowledge graph.
    ```bash
    # Set your OpenAI API Key first
    # Windows (PowerShell): $env:QDB_CODEX_API_KEY="sk-..."
    # Mac/Linux: export QDB_CODEX_API_KEY="sk-..."
    
    python -m dev_brain.codex_ingest
    ```

3.  **Start the Server**:
    ```bash
    python -m dev_brain.cli_server
    ```
    Server runs on `http://127.0.0.1:8000`.

4.  **Install VS Code Extension**:
    -   Go to `dev-brain-vscode/`.
    -   Run `npm install` then `vsce package`.
    -   Install the `.vsix` file in VS Code.
    -   Open a Python file and run command: `Dev Brain: Run Cycle for Current File`.

## The Problem & Solution

### Example

**Without Dev Brain:**
> **User**: "Add user registration function"
> **AI**: *Generates direct SQL queries in the service layer* ❌
> *(Violates architectural separation of concerns)*

**With Dev Brain:**
> **User**: "Add user registration function"
> **Dev Brain Injects**: "Context: Service layer detected. Rule DEC-005 applies: No direct SQL allowed. Use `UserRepository` pattern."
> **AI**: *Generates compliant code using `UserRepository`* ✅

## Architecture

The system consists of three main components:

1.  **The Vault (`.dev_brain/`)**: A local JSON-based knowledge graph.
2.  **The Guardian**: Analyzes changes and updates compliance beliefs.
3.  **The Composer**: Generates governance-aware prompts.

### Vault Structure (JSON)

The brain stores knowledge in `.dev_brain/`:

```json
// decisions.json (The Rules)
[
  {
    "id": "DEC-005",
    "rule": "No direct SQL in Service Layers",
    "status": "strict",
    "amplitude": 0.9
  }
]

// rule_states/services_payment_service.json (The Beliefs)
{
  "file": "services/payment_service.py",
  "rule_states": [
    {
      "rule_id": "DEC-005",
      "state_belief": {
        "compliant": 0.0,
        "at_risk": 0.4,
        "violating": 0.6
      }
    }
  ]
}
```

## Technical Details

-   **Python Version**: 3.10+
-   **Node.js Version**: 16+ (for VS Code extension)
-   **Server Port**: 8000 (Default)
-   **API**: RESTful API built with FastAPI.
    -   `POST /run-cycle`: Triggers the full Guardian-Composer pipeline.

## Roadmap

- [ ] **Rule Learning**: Automatically infer rules from existing code patterns.
- [ ] **Multi-repo Support**: Share a "Brain" across multiple microservices.
- [ ] **Git Integration**: Evolve rules based on PR reviews and commit history.
- [ ] **Plugin System**: Support for custom static analysis engines.

## Contributing

We welcome contributions! Please follow these steps:
1.  Fork the repository.
2.  Create a feature branch.
3.  Submit a Pull Request.

## License

MIT License. See `LICENSE` file for details.

---

### FAQ

**Q: How are rules defined?**
A: Currently, rules are defined manually in `.dev_brain/decisions.json`. Future versions will support learning rules from code.

**Q: Does it support multiple languages?**
A: The core logic is language-agnostic. The current implementation focuses on Python for parsing/summarization, but can be extended to TS/JS, Go, etc.

**Q: What is the performance overhead?**
A: Minimal. The "Brain" runs asynchronously. The VS Code extension waits for the prompt generation (usually 1-2 seconds), but the heavy lifting (updating the graph) happens in the background.
