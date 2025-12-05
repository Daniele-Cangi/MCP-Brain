import os
from pathlib import Path
from .vault_io import load_decisions, load_file_summary, load_rule_states
from .governance import build_governance_state_block

def generate_prompt(user_request: str, target_file: str) -> str:
    """
    Generates a governance-aware prompt for the coding LLM.
    """
    
    # 1. Read target file source code
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            target_source = f.read()
    except FileNotFoundError:
        target_source = "(File not found, assuming new file creation)"
    
    # 2. Load knowledge
    file_summary = load_file_summary(target_file)
    decisions = load_decisions()
    rule_states = load_rule_states(target_file)
    
    # 3. Build Governance Block
    governance_block = build_governance_state_block(target_file, decisions, rule_states)
    
    # 4. Build Dependency View (Interface View)
    dependency_block = ""
    if file_summary and file_summary.lenses.interface_view:
        deps = file_summary.lenses.interface_view.dependencies
        if deps:
            dependency_block = "\n[DEPENDENCIES] Interface Views:\n"
            for dep in deps:
                # In a real system, we'd resolve the file path for the dependency class
                # For MVP, we'll just list the dependency name
                dependency_block += f"- {dep} (Interface details would be loaded here)\n"
    
    # 5. Assemble Prompt
    prompt = f"""SYSTEM:
Role: "You are Nexus, a Senior Architect assistant. You act as a gatekeeper for code quality and architectural consistency."

KNOWLEDGE GRAPH (Context Lensing Active):

[TARGET] {target_file} with full source code:
```python
{target_source}
```

{dependency_block}
{governance_block}

USER REQUEST:
{user_request}

INSTRUCTIONS:
1. If the user request conflicts with any decision above, DO NOT implement the forbidden pattern.
2. Explain which decision is being violated (by ID).
3. Prefer changes that increase the "compliant" probability for critical rules.
4. If you propose multiple refactorings, annotate which option best reduces overall risk.
"""
    return prompt
