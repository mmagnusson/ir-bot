#!/usr/bin/env python3
"""
Quick test script for the incident classifier
Tests keyword-based classification without requiring AI API
"""

import sys
sys.path.insert(0, '.')

from app.services.classifier import IncidentClassifier
from app.models.incident import IncidentType

def test_classifier():
    """Test the classifier with various incident scenarios"""

    classifier = IncidentClassifier()

    test_cases = [
        {
            "name": "Ransomware",
            "data": "Multiple users reporting files encrypted with .locked extension. Ransom note found on desktop demanding 5 BTC payment. File server shows mass file modifications in last 30 minutes. Backup system also affected.",
            "expected": IncidentType.RANSOMWARE
        },
        {
            "name": "Phishing",
            "data": "User reported suspicious email from sender claiming to be IT support. Email requested user to click link and verify credentials. Link points to fake-microsoft-login.com domain. User did not click the link.",
            "expected": IncidentType.PHISHING
        },
        {
            "name": "DDoS",
            "data": "Website experiencing severe slowdown. Network monitoring shows traffic spike from 2 Gbps to 45 Gbps. Traffic appears to be SYN flood from multiple source IPs. Service is currently unavailable to users.",
            "expected": IncidentType.DDOS
        },
        {
            "name": "Account Compromise",
            "data": "Multiple failed SSH login attempts detected. 127 attempts in 5 minutes from suspicious IP address. Successful login after failed attempts. Unusual commands executed: whoami, cat /etc/shadow.",
            "expected": IncidentType.ACCOUNT_COMPROMISE
        },
        {
            "name": "Malware",
            "data": "User system running slow with unknown processes. Suspicious executable found in temp directory. Process making outbound connections to unknown IP. Registry modifications detected.",
            "expected": IncidentType.MALWARE
        },
        {
            "name": "Data Breach",
            "data": "Database accessed by unauthorized query. SQL injection attack successful. Customer PII data downloaded. 50,000 records compromised including SSN and credit cards.",
            "expected": IncidentType.DATA_BREACH
        },
        {
            "name": "Insider Threat",
            "data": "Employee accessed sensitive files outside normal duties. Bulk download of customer database to USB drive detected. User is resigning next week. Off-hours access to financial records.",
            "expected": IncidentType.INSIDER_THREAT
        },
        {
            "name": "Unauthorized Access",
            "data": "Privilege escalation detected on production server. Unknown user gained root access via vulnerability exploit. Backdoor account created. Lateral movement to other systems observed.",
            "expected": IncidentType.UNAUTHORIZED_ACCESS
        }
    ]

    print("Testing Incident Classifier (Keyword-Based)")
    print("=" * 60)
    print()

    passed = 0
    failed = 0

    for test in test_cases:
        print(f"Test: {test['name']}")
        print(f"Data: {test['data'][:80]}...")

        # Get keyword-based classification
        scores = classifier.keyword_based_classification(test['data'])

        # Find top classification
        top_type = max(scores.items(), key=lambda x: x[1])

        # Check if it matches expected
        success = top_type[0] == test['expected']

        status = "✓ PASS" if success else "✗ FAIL"
        print(f"Result: {top_type[0].value} (confidence: {top_type[1]:.0f}%)")
        print(f"Expected: {test['expected'].value}")
        print(f"Status: {status}")
        print()

        if success:
            passed += 1
        else:
            failed += 1
            print(f"  Top 3 scores:")
            top_3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
            for itype, score in top_3:
                print(f"    - {itype.value}: {score:.0f}%")
            print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"Accuracy: {(passed/len(test_cases)*100):.1f}%")

    return passed == len(test_cases)

if __name__ == "__main__":
    success = test_classifier()
    sys.exit(0 if success else 1)
