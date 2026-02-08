# Insurance Claims Processing Pipeline

A lightweight, rule-based system for processing FNOL (First Notice of Loss) documents and routing insurance claims.

## Overview

This is a production-oriented prototype that extracts key information from claim documents, identifies missing mandatory fields, and routes claims to appropriate workflows based on deterministic business rules.

## Features

- **Field Extraction**: Uses regex patterns to extract 15+ fields from unstructured text
- **Validation**: Identifies missing mandatory fields
- **Smart Routing**: Applies prioritized business rules for claim routing
- **Explainability**: Provides clear reasoning for every routing decision
- **JSON Output**: Structured, machine-readable results

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd SF_Assignment

# No external dependencies required for TXT processing
# PDF processing requires one optional dependency:
pip install PyPDF2
# or
pip install pdfplumber
```

## Usage

### Process a Single Claim

```bash
python claims_processor.py sample_claims/claim_fasttrack.txt
```

### Test All Sample Claims

```bash
python test_claims.py
```

### Programmatic Usage

```python
from claims_processor import process_claim

result = process_claim("path/to/claim.txt")
print(result)
```

## Design Choices

### 1. Rule-Based Extraction
- **Why**: Simple, transparent, and maintainable for junior developers
- **How**: Regex patterns match common FNOL document structures
- **Trade-off**: Less flexible than ML but more explainable and debuggable

### 2. Deterministic Routing
- **Why**: Insurance routing must be consistent and auditable
- **How**: Rules applied in strict priority order (see below)
- **Trade-off**: Cannot learn from data but guarantees predictable behavior

### 3. Minimal Dependencies
- **Why**: Easier deployment and fewer security vulnerabilities
- **How**: Uses only Python standard library for text processing
- **Trade-off**: PDF support requires optional external library

## Routing Rules (Priority Order)

The system applies rules in this exact sequence. Priority order follows risk management principles: **Risk → Completeness → Specialization → Speed**

1. **Investigation Flag** (Highest Priority)
   - Trigger: Description contains "fraud", "staged", or "inconsistent"
   - Reason: Fraud risk overrides all other considerations
   - Priority: Risk management takes absolute precedence

2. **Manual Review**
   - Trigger: Any mandatory field is missing
   - Reason: Incomplete data blocks automation
   - Priority: Data completeness required before any routing decision

3. **Specialist Queue**
   - Trigger: Claim type contains "injury"
   - Reason: Bodily injury requires medical expertise regardless of claim value
   - Priority: Specialization needs trump efficiency (e.g., $5K injury → Specialist, not Fast-track)

4. **Fast-track**
   - Trigger: Estimated damage < $25,000
   - Reason: Low-value, complete, non-injury claims can be processed quickly
   - Priority: Efficiency optimization only when risk/completeness/specialization satisfied

5. **Manual Review** (Default)
   - Trigger: High-value claims (≥ $25,000) without other flags
   - Reason: High-value claims need careful assessment

**Conflict Resolution**: Rules are deterministic and mutually exclusive by design. When multiple conditions could apply, strict priority order ensures consistent routing.

## Mandatory Fields

The following fields must be present for auto-processing:
- `policy_number`
- `policyholder_name`
- `incident_date`
- `incident_description` (required for fraud detection and routing logic)
- `claim_type`
- `estimated_damage`

Note: Some fields (e.g., `incident_description`) are elevated to mandatory due to routing dependencies.

## Output Format

```json
{
  "extractedFields": {
    "policy_number": "POL-2024-001234",
    "policyholder_name": "John Smith",
    "incident_date": "03/15/2024",
    "estimated_damage": 8500.0,
    "claim_type": "Property Damage",
    ...
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "Estimated damage ($8,500.00) is below $25,000 threshold"
}
```

## Sample Claims

The `sample_claims/` directory contains 6 test cases covering all routing scenarios:

1. **claim_fasttrack.txt** - Low-value property damage → Fast-track
2. **claim_injury.txt** - Bodily injury (medium value) → Specialist Queue
3. **claim_conflict_case.txt** - Low-value injury ($4,500) → Specialist Queue (demonstrates priority: specialization > speed)
4. **claim_fraud_flag.txt** - Fraud indicators → Investigation Flag
5. **claim_missing_fields.txt** - Incomplete data → Manual Review
6. **claim_high_value.txt** - High-value claim → Manual Review

## Known Limitations

### Current Limitations

1. **Document Format**
   - Only supports structured text with labeled fields
   - Requires consistent field naming (e.g., "Policy Number:", "Incident Date:")
   - PDF support requires additional library installation

2. **Extraction Accuracy**
   - Regex patterns assume standard formatting
   - Field extraction assumes reasonably consistent FNOL labels (e.g., "Policy Number:", "Incident Date:")
   - Real-world deployments would require schema normalization or ML-assisted entity extraction
   - May fail on unusual date formats or field variations
   - Cannot handle handwritten or scanned documents without OCR

3. **Language Support**
   - English only
   - No support for multilingual documents

4. **Field Validation**
   - No semantic validation (e.g., date logic, policy number format)
   - No cross-field consistency checks

5. **Routing Logic**
   - Fixed rules cannot adapt to new patterns
   - No confidence scoring or uncertainty handling

## Future Enhancements

### Short-term (Production Hardening)

1. **Enhanced Validation**
   - Date range validation (incident date within policy period)
   - Policy number format verification
   - Damage estimate reasonableness checks

2. **Better Error Handling**
   - Graceful degradation for partially readable documents
   - Detailed error logging and reporting

3. **Configuration**
   - Externalize routing rules to JSON/YAML config
   - Configurable mandatory fields per claim type
   - Adjustable damage threshold

### Medium-term (Scale)

1. **Batch Processing**
   - Process multiple claims in parallel
   - Generate summary reports
   - Database integration for claim tracking

2. **API Wrapper**
   - REST API for integration with other systems
   - Webhook support for async processing

3. **Document Preprocessing**
   - OCR integration for scanned documents
   - PDF text extraction with layout analysis
   - Image attachment processing

### Long-term (Intelligence)

1. **Machine Learning Enhancement**
   - NER (Named Entity Recognition) for field extraction
   - Classification models for claim type prediction
   - Anomaly detection for fraud indicators

2. **Adaptive Routing**
   - Learn optimal routing from historical outcomes
   - Confidence scoring for routing decisions
   - A/B testing framework for rule optimization

3. **Advanced Features**
   - Multi-language support
   - Real-time processing pipeline
   - Integration with external data sources (weather, traffic, etc.)

## Testing

Run the test suite:

```bash
python test_claims.py
```

Expected output: 6 processed claims demonstrating all routing scenarios including conflict resolution.

## Project Structure

```
SF_Assignment/
├── claims_processor.py      # Main processing logic
├── test_claims.py           # Test script
├── README.md                # This file
├── requirements.txt         # Optional dependencies
└── sample_claims/           # Sample FNOL documents
    ├── claim_fasttrack.txt
    ├── claim_injury.txt
    ├── claim_conflict_case.txt
    ├── claim_fraud_flag.txt
    ├── claim_missing_fields.txt
    └── claim_high_value.txt
```

## Production Readiness

This is a production-oriented prototype suitable for demonstrating core logic. For actual production deployment, add:
- Comprehensive unit tests with edge case coverage
- Structured logging framework (e.g., Python logging module)
- Input sanitization and schema validation
- Error handling with graceful degradation
- Configuration management (externalized rules)
- CI/CD pipeline with automated testing

## License

Educational/Assignment Use Only
