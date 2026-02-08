"""
Test script to process all sample claims and display results.
"""

import json
from pathlib import Path
from claims_processor import process_claim


def test_all_claims():
    """Process all sample claims and print results."""
    sample_dir = Path("sample_claims")
    
    if not sample_dir.exists():
        print("Error: sample_claims directory not found")
        return
    
    claim_files = sorted(sample_dir.glob("*.txt"))
    
    if not claim_files:
        print("No claim files found in sample_claims directory")
        return
    
    print("=" * 80)
    print("INSURANCE CLAIMS PROCESSING PIPELINE - TEST RESULTS")
    print("=" * 80)
    
    for claim_file in claim_files:
        print(f"\n\nProcessing: {claim_file.name}")
        print("-" * 80)
        
        try:
            result = process_claim(str(claim_file))
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error processing {claim_file.name}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("Processing complete")
    print("=" * 80)


if __name__ == "__main__":
    test_all_claims()
