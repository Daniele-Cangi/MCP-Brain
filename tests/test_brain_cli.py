import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from pathlib import Path
import tempfile
import shutil
import os
import json

from dev_brain import brain_cli
from dev_brain.models import Decision, FrameSnapshot

class TestBrainCLI(unittest.TestCase):
    
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
            
        # Capture stdout
        self.held_stdout = sys.stdout
        self.stdout_capture = StringIO()
        sys.stdout = self.stdout_capture

    def tearDown(self):
        sys.stdout = self.held_stdout
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_status_command(self):
        # Create dummy files to count
        (self.vault_root / "rule_states" / "test.json").touch()
        (self.vault_root / "frames" / "frame_1.json").touch()
        
        args = MagicMock()
        brain_cli.cmd_status(args)
        
        output = self.stdout_capture.getvalue()
        self.assertIn("Decisions (rules): 1", output)
        self.assertIn("Files with rule_states: 1", output)
        self.assertIn("Frames: 1", output)

    def test_rules_command(self):
        args = MagicMock()
        brain_cli.cmd_rules(args)
        
        output = self.stdout_capture.getvalue()
        self.assertIn("DEC-TEST", output)
        self.assertIn("Test Rule", output)

    def test_file_command(self):
        # Create summary and rule state for a file
        target_file = "services/test.py"
        summary_path = self.vault_root / "summaries" / "services_test.json"
        with open(summary_path, "w") as f:
            f.write('{"file": "services/test.py", "hash": "dummy", "lenses": {"interface_view": {"classes": ["TestClass"], "public_methods": [], "dependencies": []}, "logic_view": {"flow": [], "critical_branches": []}, "data_view": {"reads_from": [], "writes_to": [], "side_effects": []}}, "governance_tags": ["test"]}')
            
        args = MagicMock()
        args.file_path = target_file
        brain_cli.cmd_file(args)
        
        output = self.stdout_capture.getvalue()
        self.assertIn("File: services/test.py", output)
        self.assertIn("TestClass", output)

    def test_frames_command(self):
        # Create a frame
        frame = FrameSnapshot(
            frame_id="frame_test",
            timestamp="2025-01-01T00:00:00Z",
            user_goal="Test Goal",
            changed_files=[],
            relevant_decisions=[],
            suspected_violations=[],
            predicted_risks=[],
            next_steps=[]
        )
        with open(self.vault_root / "graph.json", "w") as f:
            f.write(json.dumps({"frames": [frame.model_dump()], "edges": []}))
            
        args = MagicMock()
        args.last = 5
        brain_cli.cmd_frames(args)
        
        output = self.stdout_capture.getvalue()
        self.assertIn("frame_test", output)
        self.assertIn("Test Goal", output)

if __name__ == '__main__':
    unittest.main()
