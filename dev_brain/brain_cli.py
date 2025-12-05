import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
import json

from . import paths
from . import vault_io
from .models import Decision, FileSummary, RuleStatesForFile, FrameSnapshot
from . import graph_manager

def cmd_status(args):
    vault_root = paths.get_vault_root()
    project_root = vault_root.parent
    
    print(f">>> Dev Brain – Status <<<")
    print(f"")
    print(f"Project root: {project_root}")
    print(f"Vault root:   {vault_root}")
    print(f"")
    
    # Load decisions
    decisions = vault_io.load_decisions()
    print(f"Decisions (rules): {len(decisions)}")
    
    # Count rule states
    rule_states_dir = vault_root / "rule_states"
    rule_state_files = list(rule_states_dir.glob("*.json")) if rule_states_dir.exists() else []
    print(f"Files with rule_states: {len(rule_state_files)}")
    
    # Count frames
    frames_dir = vault_root / "frames"
    frames_files = list(frames_dir.glob("*.json")) if frames_dir.exists() else []
    print(f"Frames: {len(frames_files)}")
    print(f"")

    # Top rules analysis
    if decisions and rule_state_files:
        print("Top rules by number of associated files:")
        rule_counts = {}
        for rs_file in rule_state_files:
            try:
                rs_data = vault_io.load_rule_states_from_path(rs_file)
                # vault_io.load_rule_states expects a file path relative to something? No, it takes absolute path if we look at implementation?
                # Actually vault_io.load_rule_states takes a Path object.
                # But wait, vault_io.load_rule_states logic:
                # def load_rule_states(file_path: Path) -> Optional[RuleStatesForFile]:
                #     return RuleStatesForFile.model_validate_json(file_path.read_text())
                if rs_data:
                    for rs in rs_data.rule_states:
                        rule_counts[rs.rule_id] = rule_counts.get(rs.rule_id, 0) + 1
            except Exception:
                continue

        # Sort by count desc
        sorted_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Create map for rule descriptions
        rule_desc_map = {d.id: d.rule for d in decisions}
        
        for rule_id, count in sorted_rules[:5]:
            desc = rule_desc_map.get(rule_id, "Unknown Rule")
            print(f"- {rule_id} ({desc}) – {count} files")

def cmd_rules(args):
    decisions = vault_io.load_decisions()
    if not decisions:
        print("No decisions found.")
        return

    print(f">>> Dev Brain – Rules <<<")
    print(f"")
    
    # Aggregate stats
    vault_root = paths.get_vault_root()
    rule_states_dir = vault_root / "rule_states"
    rule_stats = {} # rule_id -> {compliant: [], at_risk: [], violating: []}
    
    if rule_states_dir.exists():
        for rs_file in rule_states_dir.glob("*.json"):
            try:
                rs_data = vault_io.load_rule_states_from_path(rs_file)
                if rs_data:
                    for rs in rs_data.rule_states:
                        if rs.rule_id not in rule_stats:
                            rule_stats[rs.rule_id] = {"compliant": [], "at_risk": [], "violating": []}
                        
                        rule_stats[rs.rule_id]["compliant"].append(rs.state_belief.compliant)
                        rule_stats[rs.rule_id]["at_risk"].append(rs.state_belief.at_risk)
                        rule_stats[rs.rule_id]["violating"].append(rs.state_belief.violating)
            except Exception:
                continue

    for d in decisions:
        print(f"- {d.id} – {d.rule}")
        stats = rule_stats.get(d.id)
        if stats:
            count = len(stats["compliant"])
            print(f"  Files: {count}")
            if count > 0:
                avg_c = sum(stats["compliant"]) / count
                avg_r = sum(stats["at_risk"]) / count
                avg_v = sum(stats["violating"]) / count
                print(f"  Avg state (compliant / at_risk / violating):")
                print(f"    {avg_c:.2f} / {avg_r:.2f} / {avg_v:.2f}")
        else:
            print(f"  Files: 0")
        print("")

def cmd_file(args):
    target_file = args.file_path
    print(f">>> Dev Brain – File View <<<")
    print(f"")
    print(f"File: {target_file}")
    print(f"")
    
    # Summary
    summary_path = paths.summary_path_for(target_file)
    if summary_path.exists():
        try:
            summary = vault_io.load_file_summary(target_file)
            if summary:
                print("Summary:")
                if summary.lenses.interface_view.classes:
                    print(f"  - Classes: {', '.join(summary.lenses.interface_view.classes)}")
                if summary.lenses.interface_view.public_methods:
                    print(f"  - Public methods: {', '.join(summary.lenses.interface_view.public_methods)}")
                if summary.governance_tags:
                    print(f"  - Tags: {', '.join(summary.governance_tags)}")
        except Exception as e:
            print(f"Error loading summary: {e}")
    else:
        print("No summary found for this file. Run codex_ingest first.")
    
    print(f"")
    
    # Governance State
    rule_states_path = paths.rule_state_path_for(target_file)
    decisions = vault_io.load_decisions()
    decision_map = {d.id: d.rule for d in decisions}
    
    if rule_states_path.exists():
        try:
            rs_data = vault_io.load_rule_states(target_file)
            if rs_data and rs_data.rule_states:
                print("Governance state (per rule):")
                for rs in rs_data.rule_states:
                    rule_desc = decision_map.get(rs.rule_id, "Unknown Rule")
                    print(f"  - {rs.rule_id} ({rule_desc}):")
                    print(f"      compliant: {rs.state_belief.compliant:.2f}")
                    print(f"      at_risk:   {rs.state_belief.at_risk:.2f}")
                    print(f"      violating: {rs.state_belief.violating:.2f}")
            else:
                print("No active rule states for this file.")
        except Exception as e:
             print(f"Error loading rule states: {e}")
    else:
        print("No rule_states found for this file.")

def cmd_frames(args):
    limit = args.last
    print(f">>> Dev Brain – Frames (last {limit}) <<<")
    print(f"")
    
    graph = graph_manager.load_graph()
    if not graph.frames:
        print("No frames found.")
        return
        
    # Sort frames by timestamp descending
    sorted_frames = sorted(graph.frames, key=lambda f: f.timestamp, reverse=True)
    
    for frame in sorted_frames[:limit]:
        print(f"- {frame.frame_id}")
        print(f"  Time: {frame.timestamp}")
        # Truncate user request
        req = frame.user_goal
        if len(req) > 80:
            req = req[:77] + "..."
        print(f"  Event: user_request=\"{req}\"")
        
        # Target file (changed files)
        if frame.changed_files:
             print(f"  Target file: {', '.join(frame.changed_files)}")
        
        # Rules touched (relevant decisions)
        if frame.relevant_decisions:
            print(f"  Rules touched: {', '.join(frame.relevant_decisions)}")
        print("")

def main():
    parser = argparse.ArgumentParser(description="Dev Brain CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommands")
    
    # Status
    subparsers.add_parser("status", help="Show global vault status")
    
    # Rules
    subparsers.add_parser("rules", help="Show governance rules and stats")
    
    # File
    file_parser = subparsers.add_parser("file", help="Show governance state for a specific file")
    file_parser.add_argument("file_path", help="Workspace-relative path to the file")
    
    # Frames
    frames_parser = subparsers.add_parser("frames", help="Show recent frames")
    frames_parser.add_argument("--last", type=int, default=10, help="Number of frames to show")
    
    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status(args)
    elif args.command == "rules":
        cmd_rules(args)
    elif args.command == "file":
        cmd_file(args)
    elif args.command == "frames":
        cmd_frames(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
