import unittest
from pathlib import Path
import json
import tempfile
import shutil
import os

from dev_brain.models import Decision, FileSummary, RuleStatesForFile
from dev_brain.governance import select_relevant_decisions, build_governance_state_block
from dev_brain.composer import generate_prompt
from dev_brain import paths

class TestDevBrain(unittest.TestCase):
    
    def setUp(self):
        # Create a temporary directory for the vault
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Setup vault structure
        self.vault_root = Path(self.test_dir) / ".dev_brain"
        self.vault_root.mkdir()
        (self.vault_root / "summaries").mkdir()
        (self.vault_root / "rule_states").mkdir()
        (self.vault_root / "frames").mkdir()
        
        # Create services directory for test files
        (Path(self.test_dir) / "services").mkdir()
        
        # Create dummy decision
        self.decision = Decision(
            id="DEC-TEST",
            topic="Test Topic",
            rule="Test Rule",
            allowed_pattern="Allowed",
            forbidden_pattern="Forbidden",
            status="strict",
            scope_layer="architecture",
            amplitude=0.9
        )
        with open(self.vault_root / "decisions.json", "w") as f:
            f.write(json.dumps([self.decision.model_dump()]))
            
    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_paths(self):
        self.assertEqual(paths.get_vault_root(), self.vault_root)
        
    def test_governance_selection(self):
        decisions = [self.decision]
        relevant = select_relevant_decisions("any_file.py", decisions, None)
        self.assertEqual(len(relevant), 1)
        self.assertEqual(relevant[0].id, "DEC-TEST")
        
    def test_composer_prompt_generation(self):
        # Create a dummy target file
        target_file = "test_service.py"
        with open(target_file, "w") as f:
            f.write("def foo(): pass")
            
        # Generate prompt
        prompt = generate_prompt("Fix this", target_file)
        
        self.assertIn("SYSTEM:", prompt)
        self.assertIn("KNOWLEDGE GRAPH", prompt)
        self.assertIn("DEC-TEST", prompt) # Should be included as it's high amplitude
        self.assertIn("def foo(): pass", prompt)

    def test_metrics_heuristics(self):
        from dev_brain.metrics import initial_state_belief, update_state_belief_for_request
        
        initial = initial_state_belief()
        
        # 1. Neutral request
        updated_neutral = update_state_belief_for_request(initial, "Just refactoring", self.decision)
        self.assertEqual(updated_neutral.compliant, initial.compliant)
        
        # 2. Violation request (SQL)
        # Decision topic is "Test Topic", let's change it to "Data Access" for this test
        self.decision.topic = "Data Access"
        updated_violation = update_state_belief_for_request(initial, "I need to run a raw query", self.decision)
        self.assertLess(updated_violation.compliant, initial.compliant)
        self.assertGreater(updated_violation.violating, initial.violating)
        
        # 3. Confession request
        updated_confession = update_state_belief_for_request(initial, "I know it violates the rule", self.decision)
        self.assertLess(updated_confession.compliant, updated_violation.compliant) # Should be even stronger

    def test_pipeline(self):
        from dev_brain.pipeline import run_cycle
        
        # Ensure target file exists
        target_file = "services/test_pipeline.py"
        (self.vault_root / "rule_states" / "services_test_pipeline.json").touch()
        with open(target_file, "w") as f:
            f.write("code")
            
        frame_id, prompt = run_cycle("Test Pipeline", target_file)
        
        self.assertTrue(frame_id.startswith("frame_"))
        self.assertIn("GOVERNANCE STATE", prompt)
        self.assertIn("Test Pipeline", prompt)

    def test_graph_manager(self):
        from dev_brain import graph_manager
        from dev_brain.models import Graph, FrameSnapshot
        
        # Test save/load empty
        graph = graph_manager.load_graph()
        self.assertEqual(len(graph.frames), 0)
        
        # Test add frame
        frame = FrameSnapshot(
            frame_id="frame_test",
            timestamp="2025-01-01T00:00:00Z",
            user_goal="test",
            changed_files=[],
            relevant_decisions=[],
            suspected_violations=[],
            predicted_risks=[],
            next_steps=[]
        )
        graph_manager.add_frame_node(graph, frame)
        graph_manager.save_graph(graph)
        
        loaded_graph = graph_manager.load_graph()
        self.assertEqual(len(loaded_graph.frames), 1)
        self.assertEqual(loaded_graph.frames[0].frame_id, "frame_test")

    def test_api(self):
        from fastapi.testclient import TestClient
        from dev_brain.server import app
        
        client = TestClient(app)
        
        # Test Health
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")
        
        # Test Run Cycle
        # Ensure target file exists
        target_file = "services/test_api.py"
        (self.vault_root / "rule_states" / "services_test_api.json").touch()
        with open(target_file, "w") as f:
            f.write("api code")
            
        payload = {
            "user_request": "Test API",
            "target_file": target_file
        }
        
        resp = client.post("/run-cycle", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["frame_id"].startswith("frame_"))
        self.assertIn("GOVERNANCE STATE", data["prompt"])

    def test_coder_agent(self):
        from unittest.mock import patch, MagicMock
        from dev_brain.coder_agent import call_coder_llm
        
        # Mock OpenAI client
        with patch("dev_brain.coder_agent.get_openai_client") as mock_get_client:
            mock_client = MagicMock()
            mock_completion = MagicMock()
            mock_completion.choices[0].message.content = "Mocked Response"
            mock_client.chat.completions.create.return_value = mock_completion
            mock_get_client.return_value = mock_client
            
            # Set dummy API key env var for the test
            with patch.dict(os.environ, {"QDB_CODEX_API_KEY": "dummy"}):
                response = call_coder_llm("Test Prompt")
                
            self.assertEqual(response, "Mocked Response")
            mock_client.chat.completions.create.assert_called_once()
            
            # Verify system prompt was sent
            call_args = mock_client.chat.completions.create.call_args
            messages = call_args.kwargs["messages"]
            self.assertEqual(messages[0]["role"], "system")
            self.assertIn("CODER AGENT", messages[0]["content"])

    def test_codex_brain(self):
        from unittest.mock import patch, MagicMock
        from dev_brain.codex_brain import build_summary_for_file
        from pathlib import Path
        
        # Mock OpenAI client
        with patch("dev_brain.codex_brain.get_openai_client") as mock_get_client:
            mock_client = MagicMock()
            mock_completion = MagicMock()
            
            # Mock JSON response
            mock_json = """
            {
                "lenses": {
                    "interface_view": {"classes": ["CodexClass"], "public_methods": [], "dependencies": []},
                    "logic_view": {"flow": [], "critical_branches": []},
                    "data_view": {"reads_from": [], "writes_to": [], "side_effects": []}
                },
                "governance_tags": ["codex"]
            }
            """
            mock_completion.choices[0].message.content = mock_json
            mock_client.chat.completions.create.return_value = mock_completion
            mock_get_client.return_value = mock_client
            
            # Mock file reading
            with patch("pathlib.Path.read_text", return_value="class CodexClass: pass"):
                 # Set dummy API key env var
                with patch.dict(os.environ, {"QDB_CODEX_API_KEY": "dummy"}):
                    summary = build_summary_for_file(Path("codex_test.py"))
                
            self.assertEqual(summary.file, "codex_test.py")
            self.assertEqual(summary.lenses.interface_view.classes, ["CodexClass"])
            self.assertEqual(summary.governance_tags, ["codex"])

    def test_guardian_process(self):
        from dev_brain.guardian import process_change_event
        
        # Create a dummy file to be "changed"
        test_file = "services/test_service.py"
        (self.vault_root / "rule_states" / "services_test_service.json").touch() # Ensure dir exists? No, vault_io handles it? 
        # Actually vault_io expects the file to exist for load_rule_states to return something, 
        # but process_change_event handles missing rule states gracefully.
        
        # Run process
        frame_id = process_change_event("Test Goal", [test_file])
        
        self.assertTrue(frame_id.startswith("frame_"))
        self.assertTrue((self.vault_root / "frames" / f"{frame_id}.json").exists())
        
        # Check graph updated
        from dev_brain.graph_manager import load_graph
        graph = load_graph()
        self.assertTrue(any(f.frame_id == frame_id for f in graph.frames))

if __name__ == '__main__':
    unittest.main()
