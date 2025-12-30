"""Debug script to check what the playbook engine is loading"""
import yaml
from pathlib import Path

playbook_path = Path(__file__).parent / "app" / "data" / "playbooks" / "ddos.yaml"

with open(playbook_path, 'r') as f:
    playbook = yaml.safe_load(f)

print("=== DDOS Playbook Debug ===")
print(f"\nIncident Type: {playbook.get('incident_type')}")
print(f"\nIntake Phase Required Fields:")
intake_phase = playbook.get('phases', {}).get('intake', {})
required_fields = intake_phase.get('required_fields', [])
print(required_fields)

print(f"\nFull Intake Phase:")
import json
print(json.dumps(intake_phase, indent=2, default=str))
