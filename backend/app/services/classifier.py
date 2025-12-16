"""
Incident Classification Service
Uses AI to analyze raw data and suggest incident types
"""

from typing import List, Dict
import json
import re
from ..models.incident import (
    IncidentType,
    IncidentTypeClassification,
    IncidentClassificationResponse
)


class IncidentClassifier:
    """Classifies incidents from raw logs or descriptions"""

    # Keyword patterns for each incident type
    INCIDENT_PATTERNS = {
        IncidentType.PHISHING: [
            r"phish(?:ing)?",
            r"suspicious\s+email",
            r"spoof(?:ed|ing)?",
            r"credential\s+harvest",
            r"fake\s+login",
            r"sender\s+impersonat",
            r"malicious\s+link",
            r"email\s+attachment",
        ],
        IncidentType.MALWARE: [
            r"malware",
            r"virus",
            r"trojan",
            r"backdoor",
            r"suspicious\s+process",
            r"file\s+executed",
            r"process\s+injection",
            r"scheduled\s+task\s+created",
            r"registry\s+modification",
        ],
        IncidentType.RANSOMWARE: [
            r"ransomware",
            r"files?\s+encrypted",
            r"\.encrypted",
            r"ransom\s+note",
            r"bitcoin",
            r"payment\s+demand",
            r"all\s+files\s+locked",
            r"decryption\s+key",
        ],
        IncidentType.ACCOUNT_COMPROMISE: [
            r"account\s+compromise",
            r"unauthorized\s+(?:access|login)",
            r"impossible\s+travel",
            r"suspicious\s+sign-?in",
            r"password\s+spray",
            r"brute\s+force",
            r"multiple\s+failed\s+login",
            r"unusual\s+location",
        ],
        IncidentType.DATA_BREACH: [
            r"data\s+breach",
            r"data\s+exfiltration",
            r"unauthorized\s+(?:download|transfer)",
            r"(?:pii|phi|pci)\s+exposed",
            r"database\s+dump",
            r"sql\s+injection",
            r"sensitive\s+data\s+accessed",
            r"records?\s+compromised",
        ],
        IncidentType.INSIDER_THREAT: [
            r"insider\s+threat",
            r"employee\s+(?:suspicious|malicious)",
            r"internal\s+user",
            r"data\s+theft",
            r"unauthorized\s+file\s+access",
            r"privilege\s+abuse",
            r"off-?hours\s+access",
            r"bulk\s+download",
        ],
        IncidentType.DDOS: [
            r"dd?os",
            r"denial\s+of\s+service",
            r"traffic\s+(?:flood|spike)",
            r"syn\s+flood",
            r"http\s+flood",
            r"(?:network|bandwidth)\s+saturation",
            r"service\s+(?:unavailable|down)",
            r"amplification\s+attack",
        ],
        IncidentType.UNAUTHORIZED_ACCESS: [
            r"unauthorized\s+access",
            r"privilege\s+escalation",
            r"lateral\s+movement",
            r"compromised\s+system",
            r"backdoor\s+access",
            r"exploit",
            r"vulnerability",
            r"remote\s+access",
        ],
    }

    @staticmethod
    def build_classification_prompt(raw_data: str, context: str = None) -> str:
        """Build prompt for AI classification"""
        incident_types_desc = """
- phishing: User-reported suspicious emails, credential harvesting attempts, email-based attacks
- malware: Malicious software infections, viruses, trojans, suspicious file execution
- ransomware: File encryption attacks, ransom demands, data held hostage
- account_compromise: Unauthorized account access, credential theft, suspicious logins
- data_breach: Unauthorized data access or exfiltration, database compromises, data exposure
- insider_threat: Malicious or negligent employee actions, internal data theft, privilege abuse
- ddos: Denial of service attacks, traffic floods, service disruptions
- unauthorized_access: System breaches, privilege escalation, unauthorized system entry
"""

        prompt = f"""You are an expert security analyst. Analyze the following incident data and classify it into the most appropriate incident type.

INCIDENT DATA:
{raw_data}
"""

        if context:
            prompt += f"\nADDITIONAL CONTEXT:\n{context}\n"

        prompt += f"""
AVAILABLE INCIDENT TYPES:
{incident_types_desc}

Provide your classification in the following JSON format:
{{
    "primary_type": "incident_type",
    "primary_confidence": 85,
    "primary_reasoning": "Brief explanation",
    "primary_indicators": ["indicator1", "indicator2"],
    "alternatives": [
        {{
            "type": "alternative_type",
            "confidence": 45,
            "reasoning": "Why this is possible",
            "indicators": ["indicator1"]
        }}
    ],
    "summary": "2-3 sentence summary of the incident",
    "next_steps": ["Immediate action 1", "Immediate action 2"]
}}

IMPORTANT:
- Confidence should be 0-100 (higher = more certain)
- Only include alternatives with confidence > 30%
- Base classification ONLY on evidence in the data
- If unclear, lower the confidence score
- Identify specific indicators that led to the classification
"""
        return prompt

    @staticmethod
    def parse_classification_response(ai_response: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from the response
            # AI might include explanation before/after JSON
            json_match = re.search(r'\{[\s\S]*\}', ai_response)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback: treat entire response as JSON
                return json.loads(ai_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, return a default structure
            return {
                "primary_type": "phishing",
                "primary_confidence": 50,
                "primary_reasoning": "Unable to parse AI response, defaulting to phishing",
                "primary_indicators": [],
                "alternatives": [],
                "summary": "Classification uncertain due to parsing error",
                "next_steps": ["Manually review the incident data"]
            }

    @staticmethod
    def keyword_based_classification(raw_data: str) -> Dict[IncidentType, float]:
        """Fallback: Simple keyword-based classification"""
        scores = {}
        raw_data_lower = raw_data.lower()

        for incident_type, patterns in IncidentClassifier.INCIDENT_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, raw_data_lower))
                score += matches * 10  # 10 points per keyword match

            # Normalize to 0-100
            scores[incident_type] = min(score, 100)

        return scores

    @staticmethod
    def build_classification_result(
        parsed_response: Dict,
        fallback_scores: Dict[IncidentType, float] = None
    ) -> IncidentClassificationResponse:
        """Build the final classification response"""

        # Map string incident types to enum
        type_mapping = {
            "phishing": IncidentType.PHISHING,
            "malware": IncidentType.MALWARE,
            "ransomware": IncidentType.RANSOMWARE,
            "account_compromise": IncidentType.ACCOUNT_COMPROMISE,
            "data_breach": IncidentType.DATA_BREACH,
            "insider_threat": IncidentType.INSIDER_THREAT,
            "ddos": IncidentType.DDOS,
            "unauthorized_access": IncidentType.UNAUTHORIZED_ACCESS,
        }

        # Build primary classification
        primary_type_str = parsed_response.get("primary_type", "phishing")
        primary_type = type_mapping.get(primary_type_str, IncidentType.PHISHING)

        primary = IncidentTypeClassification(
            incident_type=primary_type,
            confidence=float(parsed_response.get("primary_confidence", 50)),
            reasoning=parsed_response.get("primary_reasoning", "No reasoning provided"),
            key_indicators=parsed_response.get("primary_indicators", [])
        )

        # Build alternative classifications
        alternatives = []
        for alt in parsed_response.get("alternatives", []):
            alt_type_str = alt.get("type", "")
            alt_type = type_mapping.get(alt_type_str)
            if alt_type:
                alternatives.append(IncidentTypeClassification(
                    incident_type=alt_type,
                    confidence=float(alt.get("confidence", 30)),
                    reasoning=alt.get("reasoning", "Alternative classification"),
                    key_indicators=alt.get("indicators", [])
                ))

        # Sort alternatives by confidence
        alternatives.sort(key=lambda x: x.confidence, reverse=True)

        return IncidentClassificationResponse(
            primary_classification=primary,
            alternative_classifications=alternatives,
            raw_data_summary=parsed_response.get("summary", "No summary available"),
            suggested_next_steps=parsed_response.get("next_steps", [])
        )
