"""
Automated test suite for all 23 incident types
Tests incident creation with valid test data for each playbook
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://127.0.0.1:8000/api/incidents"

# Test data for each incident type
TEST_DATA = {
    "account_compromise": {
        "incident_type": "account_compromise",
        "account_compromise_data": {
            "affected_user_email": "test.user@example.com",
            "suspicious_activities": "Multiple failed login attempts followed by successful login from unusual IP address in different country"
        }
    },

    "api_security_breach": {
        "incident_type": "api_security_breach",
        "api_security_breach_data": {
            "affected_api": "https://api.example.com/v1/users",
            "attack_type": "Broken authentication - JWT token manipulation",
            "api_authentication_method": "JWT Bearer tokens"
        }
    },

    "backup_system_compromise": {
        "incident_type": "backup_system_compromise",
        "backup_system_compromise_data": {
            "backup_system_type": "Cloud-based backup (AWS S3)",
            "backup_scope": "Full system backups including databases and file servers",
            "compromise_method": "Ransomware encrypted backup files via compromised backup service account"
        }
    },

    "bec": {
        "incident_type": "bec",
        "bec_data": {
            "compromised_account_email": "cfo@example.com",
            "fraudulent_request_type": "Wire transfer request",
            "target_recipient_email": "accounting@example.com",
            "impersonated_executive": "CFO John Smith"
        }
    },

    "cloud_account_compromise": {
        "incident_type": "cloud_account_compromise",
        "cloud_account_compromise_data": {
            "cloud_provider": "AWS",
            "compromised_account_id": "123456789012",
            "account_type": "Admin account with EC2 and S3 permissions",
            "unauthorized_actions": "Created multiple EC2 instances for cryptocurrency mining"
        }
    },

    "container_compromise": {
        "incident_type": "container_compromise",
        "container_compromise_data": {
            "affected_platform": "Kubernetes",
            "compromised_component": "Pod running web application in production namespace",
            "namespace_affected": "production"
        }
    },

    "credential_stuffing": {
        "incident_type": "credential_stuffing",
        "credential_stuffing_data": {
            "affected_service": "Customer login portal",
            "attack_volume": "50,000 login attempts in 2 hours",
            "source_ips_count": 1500
        }
    },

    "data_breach": {
        "incident_type": "data_breach",
        "data_breach_data": {
            "data_type_affected": "Customer PII including names, emails, phone numbers",
            "estimated_records": 10000,
            "breach_method": "SQL injection vulnerability in customer portal",
            "time_of_discovery": datetime.utcnow().isoformat(),
            "breach_source": "Discovered during routine security audit"
        }
    },

    "data_exfiltration": {
        "incident_type": "data_exfiltration",
        "data_exfiltration_data": {
            "affected_system": "File server containing engineering documents",
            "data_classification": "Confidential - Trade secrets and intellectual property",
            "exfiltration_method": "HTTPS upload to external cloud storage",
            "estimated_data_volume": "150GB of technical documentation"
        }
    },

    "ddos": {
        "incident_type": "ddos",
        "ddos_data": {
            "affected_service": "Main company website https://example.com",
            "attack_type": "HTTP flood targeting application layer",
            "service_impacted": "yes",
            "time_of_detection": datetime.now().isoformat()
        }
    },

    "dns_hijacking": {
        "incident_type": "dns_hijacking",
        "dns_hijacking_data": {
            "affected_domain": "example.com",
            "hijack_type": "Registrar account takeover",
            "dns_provider": "Cloudflare"
        }
    },

    "insider_threat": {
        "incident_type": "insider_threat",
        "insider_threat_data": {
            "suspect_user_email": "employee@example.com",
            "suspicious_activity": "Accessing sensitive customer database outside normal working hours, downloading large datasets",
            "data_access_anomaly": "yes",
            "time_of_detection": datetime.now().isoformat()
        }
    },

    "iot_device_compromise": {
        "incident_type": "iot_device_compromise",
        "iot_device_compromise_data": {
            "device_type": "IP security cameras",
            "device_count": 15,
            "compromise_method": "Default credentials were not changed after installation, allowing remote access"
        }
    },

    "malware": {
        "incident_type": "malware",
        "malware_data": {
            "reporting_user_email": "user@example.com",
            "file_executed": "yes",
            "suspicious_behavior": "System running slowly, unknown processes consuming CPU, outbound connections to suspicious IPs"
        }
    },

    "mobile_device_compromise": {
        "incident_type": "mobile_device_compromise",
        "mobile_device_compromise_data": {
            "device_type": "iPhone 14 Pro",
            "device_ownership": "Corporate",
            "compromise_method": "User clicked on phishing link that installed malicious profile"
        }
    },

    "phishing": {
        "incident_type": "phishing",
        "phishing_data": {
            "reporting_user_email": "reporter@example.com",
            "user_clicked": "yes",
            "attachment_opened": "no",
            "credentials_entered": "yes",
            "headers_available": True
        }
    },

    "ransomware": {
        "incident_type": "ransomware",
        "ransomware_data": {
            "reporting_user_email": "victim@example.com",
            "files_encrypted": "yes",
            "ransom_note_present": "yes",
            "ransom_amount": "5 BTC (approximately $200,000)"
        }
    },

    "regulatory_compliance_incident": {
        "incident_type": "regulatory_compliance_incident",
        "regulatory_compliance_incident_data": {
            "regulation_type": "GDPR",
            "affected_data_type": "Personal Identifiable Information (PII)",
            "affected_records_count": 5000,
            "time_of_detection": datetime.now().isoformat()
        }
    },

    "saas_application_compromise": {
        "incident_type": "saas_application_compromise",
        "saas_application_compromise_data": {
            "saas_platform": "Microsoft 365",
            "compromise_type": "OAuth token abuse via malicious third-party app",
            "affected_accounts": 50
        }
    },

    "supply_chain_attack": {
        "incident_type": "supply_chain_attack",
        "supply_chain_attack_data": {
            "affected_vendor": "SolarWinds Orion",
            "compromised_component": "Orion Platform software update",
            "attack_vector": "Malicious code injected into legitimate software update by threat actor"
        }
    },

    "unauthorized_access": {
        "incident_type": "unauthorized_access",
        "unauthorized_access_data": {
            "affected_system": "Production database server",
            "access_method": "Stolen SSH keys from developer laptop",
            "unauthorized_actions": "Attempted to export customer database, viewed configuration files"
        }
    },

    "web_application_attack": {
        "incident_type": "web_application_attack",
        "web_application_attack_data": {
            "affected_application": "https://portal.example.com",
            "attack_type": "SQL injection",
            "attack_vector": "Malicious input in search parameter allowing database query manipulation"
        }
    },

    "zero_day_exploit": {
        "incident_type": "zero_day_exploit",
        "zero_day_exploit_data": {
            "affected_software": "Apache Log4j 2.x",
            "vulnerability_type": "Remote Code Execution (RCE) via JNDI injection",
            "exploit_source": "Active exploitation detected in the wild (CVE-2021-44228)"
        }
    }
}

def test_incident_creation(incident_type, payload):
    """Test creating an incident with the given payload"""
    print(f"\n{'='*80}")
    print(f"Testing: {incident_type.upper().replace('_', ' ')}")
    print(f"{'='*80}")

    try:
        # Send POST request
        response = requests.post(BASE_URL, json=payload, timeout=10)

        # Check response
        if response.status_code == 200:
            incident = response.json()
            incident_id = incident.get('incident_id')
            print(f"[PASS] SUCCESS - Incident created successfully")
            print(f"   Incident ID: {incident_id}")
            print(f"   Status: {incident.get('status')}")
            print(f"   Created at: {incident.get('created_at')}")
            return True, incident_id
        else:
            print(f"[FAIL] FAILED - Status code: {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None

    except Exception as e:
        print(f"[FAIL] EXCEPTION - {str(e)}")
        return False, None

def verify_incident(incident_id):
    """Verify the incident was created by fetching it"""
    try:
        response = requests.get(f"{BASE_URL}/{incident_id}", timeout=10)
        if response.status_code == 200:
            print(f"[PASS] Verification successful - Incident retrieved")
            return True
        else:
            print(f"[FAIL] Verification failed - Could not retrieve incident")
            return False
    except Exception as e:
        print(f"[FAIL] Verification exception - {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("INCIDENT TYPE AUTOMATED TEST SUITE")
    print("Testing all 23 incident types with realistic data")
    print("="*80)

    results = {}
    successful = 0
    failed = 0

    # Test each incident type
    for incident_type, payload in TEST_DATA.items():
        success, incident_id = test_incident_creation(incident_type, payload)

        # Verify if creation was successful
        if success and incident_id:
            verified = verify_incident(incident_id)
            results[incident_type] = "PASS" if verified else "PASS (creation) / FAIL (verification)"
            if verified:
                successful += 1
            else:
                failed += 1
        else:
            results[incident_type] = "FAIL"
            failed += 1

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"\nTotal Tests: {len(TEST_DATA)}")
    print(f"Passed: {successful}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(successful/len(TEST_DATA)*100):.1f}%")

    print("\n" + "-"*80)
    print("DETAILED RESULTS")
    print("-"*80)

    for incident_type, result in sorted(results.items()):
        status_icon = "[PASS]" if result == "PASS" else "[FAIL]"
        print(f"{status_icon} {incident_type.ljust(35)} {result}")

    print("\n" + "="*80)

    if failed == 0:
        print("SUCCESS! ALL TESTS PASSED! All 23 incident types working correctly.")
    else:
        print(f"WARNING: {failed} test(s) failed. Please review the errors above.")

    print("="*80 + "\n")

    return failed == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
