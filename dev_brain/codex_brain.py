import json
import hashlib
from pathlib import Path
from typing import Iterable, Optional
import os
from .models import FileSummary
from .paths import summary_path_for
from .openai_client import get_openai_client

CODEX_SYSTEM_PROMPT = """You are a static analysis engine for a codebase.
Your task is to analyze a single source file and output a compact JSON summary
matching the FileSummary schema used by Dev Brain.
""".strip()

def build_summary_for_file(file_path: Path) -> FileSummary:
    """
    Generates a FileSummary for the given file using Codex.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        raise

    client = get_openai_client()
    model = os.environ.get("QDB_CODEX_MODEL", "gpt-5.1")
    
    # Calculate hash
    file_hash = f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()}"
    
    user_prompt = f"""Analyze the following file and produce a JSON object with this structure:

{{
  "file": "{file_path.as_posix()}",
  "hash": "{file_hash}",
  "lenses": {{
    "interface_view": {{
      "classes": [...],
      "public_methods": [...],
      "dependencies": [...]
    }},
    "logic_view": {{
      "flow": [...],
      "critical_branches": [...]
    }},
    "data_view": {{
      "reads_from": [...],
      "writes_to": [...],
      "side_effects": [...]
    }}
  }},
  "governance_tags": [...]
}}

Notes:
- Only output valid JSON.
- Do not include comments or explanations.
- `dependencies` should list other logical components this file depends on (by name).
- `governance_tags` can include rough tags like "service_layer", "infrastructure", "data_access", etc.

Here is the file content:

```python
{content}
```
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": CODEX_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        
        json_str = response.choices[0].message.content
        data = json.loads(json_str)
        
        # Ensure critical fields match
        data["file"] = file_path.as_posix()
        data["hash"] = file_hash
        
        return FileSummary(**data)
        
    except Exception as e:
        print(f"Error calling Codex for {file_path}: {e}")
        raise

def write_summary_to_vault(summary: FileSummary) -> Path:
    """
    Writes the summary to the vault.
    """
    # We need a Path object for summary_path_for, but it expects a string relative to root usually.
    # Let's assume summary.file is relative to project root.
    target_path = summary_path_for(summary.file)
    
    # Ensure parent dir exists
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(summary.model_dump_json(indent=2))
        
    return target_path

def ingest_files(file_paths: Iterable[Path]) -> None:
    """
    Ingests multiple files.
    """
    for p in file_paths:
        print(f"Ingesting {p}...")
        try:
            summary = build_summary_for_file(p)
            out_path = write_summary_to_vault(summary)
            print(f"  -> Written to {out_path}")
        except Exception as e:
            print(f"  -> Failed: {e}")
