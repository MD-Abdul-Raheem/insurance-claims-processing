"""
Insurance Claims Processing Pipeline
Extracts fields from FNOL documents and routes claims based on business rules.
"""

import re
import json
from typing import Dict, List, Any
from pathlib import Path


# Mandatory fields that must be present in every claim
MANDATORY_FIELDS = [
    "policy_number", "policyholder_name", "incident_date",
    "incident_description", "claim_type", "estimated_damage"
]


def extract_fields_from_text(text: str) -> Dict[str, Any]:
    """
    Extract claim fields using regex patterns.
    Returns a dictionary of extracted fields.
    """
    fields = {}
    
    # Policy Number: alphanumeric, often starts with POL or similar
    policy_match = re.search(r'Policy\s*(?:Number|#)?[:\s]+([A-Z0-9-]+)', text, re.IGNORECASE)
    if policy_match:
        fields['policy_number'] = policy_match.group(1).strip()
    
    # Policyholder Name: typically after "Policyholder" or "Insured"
    name_match = re.search(r'Policyholder(?:\s+Name)?[:\s]+([A-Za-z\s]+?)(?:\n|Policy|Effective)', text, re.IGNORECASE)
    if name_match:
        fields['policyholder_name'] = name_match.group(1).strip()
    
    # Effective Dates: date ranges
    effective_match = re.search(r'Effective\s+Date[s]?[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s*(?:to|-)\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
    if effective_match:
        fields['effective_dates'] = f"{effective_match.group(1)} to {effective_match.group(2)}"
    
    # Incident Date
    incident_date_match = re.search(r'Incident\s+Date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
    if incident_date_match:
        fields['incident_date'] = incident_date_match.group(1).strip()
    
    # Incident Time
    time_match = re.search(r'(?:Incident\s+)?Time[:\s]+(\d{1,2}:\d{2}(?:\s*[AP]M)?)', text, re.IGNORECASE)
    if time_match:
        fields['incident_time'] = time_match.group(1).strip()
    
    # Incident Location
    location_match = re.search(r'Location[:\s]+([^\n]+)', text, re.IGNORECASE)
    if location_match:
        fields['incident_location'] = location_match.group(1).strip()
    
    # Incident Description: multi-line text after "Description"
    desc_match = re.search(r'(?:Incident\s+)?Description[:\s]+([^\n]+(?:\n(?![\w\s]*:)[^\n]+)*)', text, re.IGNORECASE)
    if desc_match:
        fields['incident_description'] = desc_match.group(1).strip()
    
    # Claimant
    claimant_match = re.search(r'Claimant[:\s]+([A-Za-z\s]+?)(?:\n|Contact)', text, re.IGNORECASE)
    if claimant_match:
        fields['claimant'] = claimant_match.group(1).strip()
    
    # Third Party
    third_party_match = re.search(r'Third\s+Part(?:y|ies)[:\s]+([^\n]+)', text, re.IGNORECASE)
    if third_party_match:
        fields['third_party'] = third_party_match.group(1).strip()
    
    # Contact Details
    contact_match = re.search(r'Contact[:\s]+([^\n]+)', text, re.IGNORECASE)
    if contact_match:
        fields['contact_details'] = contact_match.group(1).strip()
    
    # Asset Type
    asset_type_match = re.search(r'Asset\s+Type[:\s]+([^\n]+)', text, re.IGNORECASE)
    if asset_type_match:
        fields['asset_type'] = asset_type_match.group(1).strip()
    
    # Asset ID
    asset_id_match = re.search(r'Asset\s+ID[:\s]+([A-Z0-9-]+)', text, re.IGNORECASE)
    if asset_id_match:
        fields['asset_id'] = asset_id_match.group(1).strip()
    
    # Estimated Damage: extract numeric value
    damage_match = re.search(r'Estimated\s+Damage[:\s]+\$?\s*([0-9,]+(?:\.\d{2})?)', text, re.IGNORECASE)
    if damage_match:
        damage_str = damage_match.group(1).replace(',', '')
        fields['estimated_damage'] = float(damage_str)
    
    # Claim Type
    claim_type_match = re.search(r'Claim\s+Type[:\s]+([^\n]+)', text, re.IGNORECASE)
    if claim_type_match:
        fields['claim_type'] = claim_type_match.group(1).strip()
    
    # Attachments
    attachments_match = re.search(r'Attachments?[:\s]+([^\n]+)', text, re.IGNORECASE)
    if attachments_match:
        fields['attachments'] = attachments_match.group(1).strip()
    
    # Initial Estimate
    initial_estimate_match = re.search(r'Initial\s+Estimate[:\s]+\$?\s*([0-9,]+(?:\.\d{2})?)', text, re.IGNORECASE)
    if initial_estimate_match:
        estimate_str = initial_estimate_match.group(1).replace(',', '')
        fields['initial_estimate'] = float(estimate_str)
    
    return fields


def identify_missing_fields(extracted_fields: Dict[str, Any]) -> List[str]:
    """
    Check which mandatory fields are missing.
    Returns a list of missing field names.
    """
    return [field for field in MANDATORY_FIELDS if field not in extracted_fields]


def determine_route(extracted_fields: Dict[str, Any], missing_fields: List[str]) -> tuple[str, str]:
    """
    Apply routing rules in priority order.
    Returns (route, reasoning) tuple.
    
    Priority follows risk management principles:
    Risk > Completeness > Specialization > Speed
    
    1. Investigation Flag - fraud indicators (HIGHEST PRIORITY - risk management)
    2. Manual Review - missing mandatory fields (data completeness required)
    3. Specialist Queue - injury claims (specialization trumps efficiency)
    4. Fast-track - low damage claims (efficiency optimization when safe)
    5. Manual Review - high-value default (conservative fallback)
    """
    
    # Rule 1: Check for fraud indicators (HIGHEST PRIORITY)
    # Fraud risk overrides all other considerations
    description = extracted_fields.get('incident_description', '').lower()
    fraud_keywords = ['fraud', 'staged', 'inconsistent']
    if any(keyword in description for keyword in fraud_keywords):
        return "Investigation Flag", "Description contains fraud indicators"
    
    # Rule 2: Check for missing mandatory fields
    # Incomplete data blocks automation - must be complete before routing
    if missing_fields:
        return "Manual Review", f"Missing mandatory fields: {', '.join(missing_fields)}"
    
    # Rule 3: Check for injury claims
    # Specialization requirement: injury needs medical expertise regardless of value
    # Example: $4,500 injury -> Specialist Queue (NOT Fast-track)
    claim_type = extracted_fields.get('claim_type', '').lower()
    if 'injury' in claim_type:
        return "Specialist Queue", "Claim involves injury and requires specialist review"
    
    # Rule 4: Fast-track for low damage claims
    # Efficiency optimization: only applies when risk/completeness/specialization satisfied
    estimated_damage = extracted_fields.get('estimated_damage', float('inf'))
    if estimated_damage < 25000:
        return "Fast-track", f"Estimated damage (${estimated_damage:,.2f}) is below $25,000 threshold"
    
    # Default: Manual Review for high-value claims
    # Conservative fallback for claims that don't match other criteria
    return "Manual Review", f"High-value claim (${estimated_damage:,.2f}) requires manual assessment"


def process_claim(file_path: str) -> Dict[str, Any]:
    """
    Main processing function.
    Reads a claim document and returns structured output.
    """
    # Read file content
    path = Path(file_path)
    if path.suffix.lower() == '.pdf':
        # For PDF files, you'd use a library like PyPDF2 or pdfplumber
        # Simplified: assume text extraction is handled
        raise NotImplementedError("PDF extraction requires PyPDF2 or pdfplumber library")
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    
    # Extract fields
    extracted_fields = extract_fields_from_text(text)
    
    # Identify missing fields
    missing_fields = identify_missing_fields(extracted_fields)
    
    # Determine routing
    route, reasoning = determine_route(extracted_fields, missing_fields)
    
    # Build output
    return {
        "extractedFields": extracted_fields,
        "missingFields": missing_fields,
        "recommendedRoute": route,
        "reasoning": reasoning
    }


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python claims_processor.py <path_to_fnol_document>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    result = process_claim(file_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
