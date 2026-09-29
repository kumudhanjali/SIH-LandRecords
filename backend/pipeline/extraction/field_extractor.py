"""
Field Extractor Module
Extracts structured land record fields from raw OCR text using schema rules and multilingual regex patterns.
Supports English, Kannada, and Telugu keyword variations with OCR noise resilience.
"""

import re
from typing import Dict, Any, List, Optional
from pipeline.extraction.schemas import get_schema_for_type


# Multilingual regex extraction rules for standard land record fields
EXTRACTION_RULES = {
    "survey_number": [
        # English: Survey No / Sy No / S.No: 142 or 142/1
        r"(?:survey\s*(?:no|number|num)?|sy\s*(?:no|num)?|s\.?\s*no\.?)\s*[:\-\s.]*\s*([0-9]+(?:\s*/\s*[0-9A-Za-z]+)?)",
        # Kannada: ಸರ್ವೆ / ಸರ್ವೇ / ಸರ್ವೆ ಸಂಖ್ಯೆ: 142/1
        r"(?:ಸರ್ವೆ|ಸರ್ವೇ|ಸರ್ವೇ\s*ಸಂಖ್ಯೆ|ಸರ್ವೆ\s*ನಂ\.?)\s*[:\-\s.]*\s*([0-9]+(?:\s*/\s*[0-9A-Za-z]+)?)",
        # Telugu: సర్వే నంబరు: 142/1
        r"(?:సర్వే\s*(?:నంబరు|సంఖ్య)?)\s*[:\-\s.]*\s*([0-9]+(?:\s*/\s*[0-9A-Za-z]+)?)",
    ],
    "hissa_number": [
        r"(?:hissa\s*(?:no|number)?|sub[- ]?division)\s*[:\-\s.]*\s*([0-9A-Za-z*]+)",
        r"(?:ಹಿಸ್ಸಾ\s*(?:ನಂ|ಸಂಖ್ಯೆ)?)\s*[:\-\s.]*\s*([0-9A-Za-z*]+)",
        r"(?:హిస్సా)\s*[:\-\s.]*\s*([0-9A-Za-z*]+)",
    ],
    "owner_name": [
        # English: Owner Name / Khatedar / Name: John Doe
        r"(?:owner\s*(?:name)?|khatedar\s*(?:name)?|occupant\s*(?:name)?|pattedar)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\u0C00-\u0C7F\s.]+?)(?=\n|$|,|survey|village|taluk|district|aadhar|aadhaar|\d{4})",
        # Kannada: ಮಾಲೀಕರ ಹೆಸರು / ಖಾತೆದಾರರ ಹೆಸರು / ಹೆಸರು
        r"(?:ಮಾಲೀಕರ\s*ಹೆಸರು|ಖಾತೆದಾರರ\s*ಹೆಸರು|ಖಾತೆದಾರರು|ಹೆಸರು)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s.]+?)(?=\n|$|,|ಗ್ರಾಮ|ತಾಲೂಕು|ಜಿಲ್ಲೆ|ವಿಸ್ತೀರ್ಣ)",
        # Telugu: యజమాని పేరు / పట్టేదారు పేరు
        r"(?:యజమాని\s*పేరు|పట్టాదారు\s*పేరు|పేరు)\s*[:\-\s.]*\s*([\u0C00-\u0C7F\s.]+?)(?=\n|$|,|గ్రామం|జిల్లా)",
    ],
    "owner_id_number": [
        # Aadhaar / UID: 12-digit number (may have 4-4-4 spacing in OCR)
        r"(?:aadhaar|aadhar|uid|id\s*(?:no|number)?)\s*[:\-\s.]*\s*(\d{4}\s?\d{4}\s?\d{4})",
        r"(?:ಆಧಾರ್|ಗುರುತಿನ\s*ಸಂಖ್ಯೆ)\s*[:\-\s.]*\s*(\d{4}\s?\d{4}\s?\d{4})",
        r"\b(\d{4}\s\d{4}\s\d{4})\b",
    ],
    "seller_name": [
        r"(?:seller\s*(?:name)?|executant|vendor)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\u0C00-\u0C7F\s.]+?)(?=\n|$|,|buyer|survey|aadhar|\d{4})",
        r"(?:ಮಾರಾಟಗಾರ(?:ರು|ರ\s*ಹೆಸರು)?)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s.]+?)(?=\n|$|,|ಖರೀದಿದಾರ|ದಿನಾಂಕ)",
    ],
    "seller_id_number": [
        r"(?:seller\s*(?:aadhaar|aadhar|id))\s*[:\-\s.]*\s*(\d{4}\s?\d{4}\s?\d{4})",
    ],
    "buyer_name": [
        r"(?:buyer\s*(?:name)?|purchaser|claimant)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\u0C00-\u0C7F\s.]+?)(?=\n|$|,|survey|village|\d{4})",
        r"(?:ಖರೀದಿದಾರ(?:ರು|ರ\s*ಹೆಸರು)?|ಖರೀದಿಗಾರ)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s.]+?)(?=\n|$|,|ದಿನಾಂಕ|ವಿಸ್ತೀರ್ಣ)",
    ],
    "buyer_id_number": [
        r"(?:buyer\s*(?:aadhaar|aadhar|id))\s*[:\-\s.]*\s*(\d{4}\s?\d{4}\s?\d{4})",
    ],
    "previous_owner": [
        r"(?:previous\s*owner|former\s*owner|transferor)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\u0C00-\u0C7F\s.]+?)(?=\n|$|,|new|survey)",
        r"(?:ಹಿಂದಿನ\s*ಮಾಲೀಕರು|ಪೂರ್ವ\s*ಖಾತೆದಾರರು)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s.]+?)(?=\n|$|,|ಹೊಸ|ದಿನಾಂಕ)",
    ],
    "new_owner": [
        r"(?:new\s*owner|transferee|successor)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\u0C00-\u0C7F\s.]+?)(?=\n|$|,|order|survey)",
        r"(?:ಹೊಸ\s*ಮಾಲೀಕರು|ನೂತನ\s*ಖಾತೆದಾರರು)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s.]+?)(?=\n|$|,|ದಿನಾಂಕ|ಆದೇಶ)",
    ],
    "new_owner_id": [
        r"(?:new\s*owner\s*(?:aadhaar|id))\s*[:\-\s.]*\s*(\d{4}\s?\d{4}\s?\d{4})",
    ],
    "village": [
        r"(?:village|vil)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\u0C00-\u0C7F\s.]+?)(?=\n|$|,|taluk|district|hobli)",
        r"(?:ಗ್ರಾಮ|ಊರು)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s.]+?)(?=\n|$|,|ತಾಲೂಕು|ಹೋಬಳಿ|ಜಿಲ್ಲೆ)",
        r"(?:గ్రామం)\s*[:\-\s.]*\s*([\u0C00-\u0C7F\s.]+?)(?=\n|$|,|మండలం|జిల్లా)",
    ],
    "taluk": [
        r"(?:taluk|taluka|tq|mandal)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\u0C00-\u0C7F\s.]+?)(?=\n|$|,|district|dist)",
        r"(?:ತಾಲೂಕು|ತಾಲ್ಲೂಕು|ತಾ\.?)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s.]+?)(?=\n|$|,|ಜಿಲ್ಲೆ|ಹೋಬಳಿ)",
        r"(?:మండలం|తాలూకా)\s*[:\-\s.]*\s*([\u0C00-\u0C7F\s.]+?)(?=\n|$|,|జిల్లా)",
    ],
    "district": [
        r"(?:district|dist)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\u0C00-\u0C7F\s.]+?)(?=\n|$|,|state|pincode|\d{6})",
        r"(?:ಜಿಲ್ಲೆ|ಜಿ\.?)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s.]+?)(?=\n|$|,|ರಾಜ್ಯ|ದಿನಾಂಕ)",
        r"(?:జిల్లా)\s*[:\-\s.]*\s*([\u0C00-\u0C7F\s.]+?)(?=\n|$|,|రాష్ట్రం)",
    ],
    "land_area": [
        # Extent: 2 Acres 15 Guntas / 2-15 / 1.5 Hectares
        r"(?:land\s*area|area|extent|total\s*extent)\s*[:\-\s.]*\s*([0-9\sA-Za-z\-.,/]+?(?:acre|acres|gunta|guntas|hectare|cents|sq\.?\s*ft|sq\.?\s*m)?)(?=\n|$|,|date|village)",
        r"(?:ವಿಸ್ತೀರ್ಣ|ವಿಸ್ತಾರ|ಒಟ್ಟು\s*ವಿಸ್ತೀರ್ಣ)\s*[:\-\s.]*\s*([0-9\s\u0C80-\u0CFF\-.,/]+?(?:ಎಕರೆ|ಗುಂಟೆ|ಸೆಂಟು|ಭಾಗ)?)(?=\n|$|,|ದಿನಾಂಕ|ಗ್ರಾಮ)",
        r"(?:విస్తీర్ణం)\s*[:\-\s.]*\s*([0-9\s\u0C00-\u0C7F\-.,/]+?(?:ఎకరాలు|గుంటలు)?)(?=\n|$|,|తేది|గ్రామం)",
    ],
    "document_date": [
        # YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
        r"(?:date|doc\s*date|issuance\s*date|date\s*of\s*issue)\s*[:\-\s.]*\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})",
        r"(?:ದಿನಾಂಕ|ದಿನಾಂಕದಂದು)\s*[:\-\s.]*\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})",
        r"(?:తేది)\s*[:\-\s.]*\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})",
    ],
    "document_number": [
        r"(?:document\s*(?:no|number)|deed\s*(?:no|number)|reg\s*(?:no|number))\s*[:\-\s.]*\s*([0-9A-Za-z/-]+)",
        r"(?:ದಸ್ತಾವೇಜು\s*ಸಂಖ್ಯೆ|ನೋಂದಣಿ\s*ಸಂಖ್ಯೆ)\s*[:\-\s.]*\s*([0-9A-Za-z/-]+)",
    ],
    "transaction_amount": [
        r"(?:transaction\s*amount|consideration|sale\s*value|amount|rs\.?|inr)\s*[:\-\s.]*\s*([0-9,]+(?:\.[0-9]{2})?)",
        r"(?:ಮೊತ್ತ|ಕ್ರಯದ\s*ಮೊತ್ತ)\s*[:\-\s.]*\s*([0-9,]+(?:\.[0-9]{2})?)",
    ],
    "execution_date": [
        r"(?:execution\s*date|reg\s*date|date\s*of\s*registration)\s*[:\-\s.]*\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})",
        r"(?:ನೋಂದಣಿ\s*ದಿನಾಂಕ)\s*[:\-\s.]*\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})",
    ],
    "mutation_number": [
        r"(?:mutation\s*(?:no|number)?|mr\s*(?:no|number)?|m\.r\.\s*no\.?)\s*[:\-\s.]*\s*([0-9A-Za-z/-]+)",
        r"(?:ಮ್ಯುಟೇಶನ್\s*ಸಂಖ್ಯೆ|ಎಂ\.?ಆರ್\.?\s*ನಂ\.?)\s*[:\-\s.]*\s*([0-9A-Za-z/-]+)",
    ],
    "mutation_type": [
        r"(?:mutation\s*type|transfer\s*type|reason)\s*[:\-\s.]*\s*([A-Za-z\u0C80-\u0CFF\s]+)",
        r"(?:ವರ್ಗಾವಣೆ\s*ವಿಧ|ಮ್ಯುಟೇಶನ್\s*ಬಗೆ)\s*[:\-\s.]*\s*([\u0C80-\u0CFF\s]+)",
    ],
    "order_date": [
        r"(?:order\s*date|sanction\s*date)\s*[:\-\s.]*\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})",
        r"(?:ಆದೇಶದ\s*ದಿನಾಂಕ|ಮಂಜೂರಾದ\s*ದಿನಾಂಕ)\s*[:\-\s.]*\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}|\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})",
    ],
    "assessment_number": [
        r"(?:assessment\s*(?:no|number)|sas\s*(?:no|number)?|appl\s*(?:no|number)?)\s*[:\-\s.]*\s*([0-9A-Za-z/-]+)",
        r"(?:ಆಕಾರ\s*ಸಂಖ್ಯೆ|ಅಸೆಸ್‌ಮೆಂಟ್\s*ನಂ\.?)\s*[:\-\s.]*\s*([0-9A-Za-z/-]+)",
    ],
    "property_id": [
        r"(?:property\s*(?:id|number)|pid\s*(?:no|number)?|e-khata\s*(?:no)?)\s*[:\-\s.]*\s*([0-9A-Za-z/-]+)",
        r"(?:ಪಿಐಡಿ|ಸ್ವತ್ತು\s*ಸಂಖ್ಯೆ)\s*[:\-\s.]*\s*([0-9A-Za-z/-]+)",
    ],
    "ward_name": [
        r"(?:ward\s*(?:no|number|name)?)\s*[:\-\s.]*\s*([0-9A-Za-z\u0C80-\u0CFF\s]+?)(?=\n|$|,|tax|owner)",
        r"(?:ವಾರ್ಡ್\s*(?:ಸಂಖ್ಯೆ|ಹೆಸರು)?)\s*[:\-\s.]*\s*([0-9A-Za-z\u0C80-\u0CFF\s]+?)(?=\n|$|,)",
    ],
    "tax_amount": [
        r"(?:tax\s*amount|total\s*tax|amount\s*paid|paid\s*amount)\s*[:\-\s.]*\s*([0-9,]+(?:\.[0-9]{2})?)",
        r"(?:ತೆರಿಗೆ\s*ಮೊತ್ತ|ಪಾವತಿಸಿದ\s*ಮೊತ್ತ)\s*[:\-\s.]*\s*([0-9,]+(?:\.[0-9]{2})?)",
    ],
    "payment_status": [
        r"(?:payment\s*status|status)\s*[:\-\s.]*\s*(Paid|Pending|Success|Failed|Unpaid|ಪಾವತಿಸಲಾಗಿದೆ)",
    ],
    "assessment_year": [
        r"(?:assessment\s*year|financial\s*year|fy|year)\s*[:\-\s.]*\s*(\d{4}(?:-\d{2,4})?)",
        r"(?:ಸಾಲಿನ\s*ವರ್ಷ|ವರ್ಷ)\s*[:\-\s.]*\s*(\d{4}(?:-\d{2,4})?)",
    ],
}


def _clean_extracted_value(value: Optional[str], field_name: str) -> Optional[str]:
    """Clean extra spaces and format specific field types like Aadhaar."""
    if not value:
        return None
    cleaned = value.strip(" :-.,\t\r\n")
    if "id_number" in field_name or field_name == "owner_id_number":
        # Standardize 12-digit ID by stripping internal spaces
        digits = re.sub(r"\D", "", cleaned)
        if len(digits) == 12:
            return digits
    return cleaned if cleaned else None


def extract_fields(ocr_text: str, document_type: str) -> Dict[str, Any]:
    """
    Extract structured fields from OCR text based on document type schema.

    Contract:
    {
        "document_type": str,
        "fields": { field_name: {"value": str | None, "raw_match": str | None} },
        "missing_required_fields": [str],
    }
    """
    schema = get_schema_for_type(document_type)

    # Graceful fallback for unknown / unmapped document types
    if not schema:
        return {
            "document_type": document_type,
            "fields": {},
            "missing_required_fields": [],
            "error": f"Unknown or unsupported document type: '{document_type}'"
        }

    extracted_fields = {}
    missing_required = []

    text_to_search = ocr_text or ""

    for field_name, field_def in schema.items():
        is_required = field_def.get("required", False)
        patterns = EXTRACTION_RULES.get(field_name, [])

        matched_value = None
        raw_match = None

        for pattern in patterns:
            match = re.search(pattern, text_to_search, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                raw_match = match.group(0)
                matched_val = match.group(1) if match.groups() else match.group(0)
                matched_value = _clean_extracted_value(matched_val, field_name)
                if matched_value:
                    break

        extracted_fields[field_name] = {
            "value": matched_value,
            "raw_match": raw_match
        }

        # Check required field status
        if is_required and (matched_value is None or matched_value == ""):
            missing_required.append(field_name)

    return {
        "document_type": document_type,
        "fields": extracted_fields,
        "missing_required_fields": missing_required
    }
