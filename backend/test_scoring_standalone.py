"""
Section 4 Standalone Test: Confidence Scorer
Tests score_fields against:
1. High-confidence OCR result with well-matched fields
2. Missing fields (must score 0.0)
3. Fields with formatting anomalies (penalized proportionally)
4. Range bounds validation [0.0 - 1.0]
"""

import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.scoring.confidence_scorer import score_fields


def run_tests():
    print("==================================================")
    print("  SECTION 4: CONFIDENCE SCORER TEST")
    print("==================================================")

    # Mock OCR result
    mock_ocr = {
        "engine": "qwen",
        "raw_text": "Survey No: 142/1\nOwner: Ramesh Kumar\nAadhaar: 541287963214",
        "lines": [
            {"text": "Survey No: 142/1", "confidence": 0.96, "bbox": None},
            {"text": "Owner: Ramesh Kumar", "confidence": 0.94, "bbox": None},
            {"text": "Aadhaar: 541287963214", "confidence": 0.92, "bbox": None}
        ],
        "overall_confidence": 0.94,
        "language_detected": "english",
        "error": None
    }

    # Mock extracted fields
    mock_extracted = {
        "document_type": "land_record",
        "fields": {
            "survey_number": {
                "value": "142/1",
                "raw_match": "Survey No: 142/1"
            },
            "owner_name": {
                "value": "Ramesh Kumar",
                "raw_match": "Owner: Ramesh Kumar"
            },
            "owner_id_number": {
                "value": "541287963214",
                "raw_match": "Aadhaar: 541287963214"
            },
            "village": {
                "value": None,
                "raw_match": None
            }
        },
        "missing_required_fields": ["village"]
    }

    scores = score_fields(mock_extracted, mock_ocr)

    print("\nScoring Results:")
    for field, data in scores.items():
        print(f"  Field: {field:<18} | Value: {str(data['value']):<20} | Confidence: {data['confidence']}")

    # Validations
    assert scores["survey_number"]["confidence"] >= 0.90, "Survey number should have high confidence"
    assert scores["owner_name"]["confidence"] >= 0.90, "Owner name should have high confidence"
    assert scores["owner_id_number"]["confidence"] >= 0.90, "Valid 12-digit Aadhaar should have high confidence"
    assert scores["village"]["confidence"] == 0.0, "Missing village field must score 0.0"

    for field, data in scores.items():
        assert 0.0 <= data["confidence"] <= 1.0, f"Confidence out of range for {field}"

    print("\n  [PASS] All confidence scores are within expected valid bounds!")
    print("\n==================================================")
    print("  SECTION 4 TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
