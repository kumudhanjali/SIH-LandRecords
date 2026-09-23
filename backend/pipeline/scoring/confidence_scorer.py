"""
Confidence Scorer Module
Calculates granular 0.0-1.0 confidence scores for extracted land record fields.
Uses an explainable, weighted linear combination of OCR base confidence,
extraction match quality, and schema format compliance.
"""

from typing import Dict, Any, Optional
import re

# Weight configuration (Sum = 1.00)
W_OCR = 0.45       # Base OCR recognition confidence
W_MATCH = 0.35     # Regex pattern match quality (exact vs fallback)
W_FORMAT = 0.20    # Format validity check


def _find_line_confidence(raw_match: Optional[str], ocr_result: Dict[str, Any]) -> float:
    """
    Locates the specific OCR line containing raw_match to retrieve line-level confidence.
    Falls back to overall OCR confidence if not found.
    """
    overall_conf = float(ocr_result.get("overall_confidence", 0.85))
    if not raw_match:
        return overall_conf

    lines = ocr_result.get("lines", [])
    raw_lower = raw_match.lower()
    for line in lines:
        line_text = line.get("text", "").lower()
        if raw_lower in line_text or line_text in raw_lower:
            return float(line.get("confidence", overall_conf))

    return overall_conf


def score_fields(extracted_fields: Dict[str, Any], ocr_result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Compute confidence score for each extracted field.

    Formula Rationale:
    -----------------
    Confidence is computed via an explainable weighted linear sum rather than compounding
    multiplication to prevent false-alarm manual review escalations on valid data:

        Confidence = (W_OCR * ocr_score) + (W_MATCH * match_quality) + (W_FORMAT * format_score)

    - If value is None or empty: Confidence = 0.0
    - OCR Score (0.0 - 1.0): Per-line OCR confidence or engine overall confidence.
    - Match Quality (0.0 - 1.0): 1.0 for clean structured regex match, 0.7 for partial match.
    - Format Score (0.0 - 1.0): 1.0 if formatted properly (e.g., 12-digit Aadhaar, valid date/number),
                                0.6 if minor anomalies exist.

    Contract:
    Returns:
    {
        field_name: {"value": ..., "confidence": float}  # 0.0 - 1.0
    }
    """
    fields_dict = extracted_fields.get("fields", {})
    scored_output = {}

    for field_name, field_info in fields_dict.items():
        value = field_info.get("value")
        raw_match = field_info.get("raw_match")

        # 1. Missing or empty fields score 0.0
        if value is None or value == "":
            scored_output[field_name] = {
                "value": None,
                "confidence": 0.0
            }
            continue

        # 2. Determine OCR base score
        ocr_conf = _find_line_confidence(raw_match, ocr_result)

        # 3. Determine match quality score
        if raw_match and len(raw_match) >= len(value):
            match_quality = 1.0
        else:
            match_quality = 0.75

        # 4. Determine format validity score
        format_score = 1.0
        if "id_number" in field_name or field_name == "owner_id_number":
            # Check 12-digit Aadhaar / UID standard
            if not re.match(r"^\d{12}$", str(value)):
                format_score = 0.50
        elif "date" in field_name:
            if not re.search(r"\d{2,4}", str(value)):
                format_score = 0.50
        elif "survey_number" in field_name:
            if not re.match(r"^[0-9]+(/[0-9A-Za-z]+)?$", str(value)):
                format_score = 0.70

        # 5. Compute combined weighted confidence
        combined_score = (W_OCR * ocr_conf) + (W_MATCH * match_quality) + (W_FORMAT * format_score)
        final_confidence = round(max(0.0, min(1.0, combined_score)), 4)

        scored_output[field_name] = {
            "value": value,
            "confidence": final_confidence
        }

    return scored_output
