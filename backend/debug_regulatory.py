"""Debug regulatory compliance incident creation"""
import requests
import json
from datetime import datetime

url = "http://127.0.0.1:8000/api/incidents/"

data = {
    "incident_type": "regulatory_compliance_incident",
    "regulatory_compliance_incident_data": {
        "regulation_type": "GDPR",
        "affected_data_type": "Personal Identifiable Information (PII)",
        "affected_records_count": 5000,
        "time_of_detection": datetime.now().isoformat()
    }
}

print("=== Sending Request ===")
print(json.dumps(data, indent=2))

response = requests.post(url, json=data)

print(f"\n=== Response Status: {response.status_code} ===")
print(response.text)
