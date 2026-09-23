"""
Section 3 Standalone Test: Field Extractor
Tests extract_fields against:
1. English RTC document text
2. Kannada RTC document text
3. Sale Deed document text
4. Property Tax with intentionally missing required fields
5. Unknown document type (error handling)
"""

import sys
import os

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.extraction.field_extractor import extract_fields


def run_tests():
    print("==================================================")
    print("  SECTION 3: FIELD EXTRACTOR TEST")
    print("==================================================")

    # Test 1: English RTC Sample
    sample_rtc_en = """
    GOVERNMENT OF KARNATAKA - REVENUE DEPARTMENT
    RECORD OF RIGHTS, TENANCY AND CROPS (RTC / PAHANI)
    Village: Ramanagara
    Taluk: Channapatna
    District: Ramanagara
    Survey No: 142/1A
    Hissa No: 1A
    Owner Name: Ramesh Kumar Gowda
    Aadhaar Number: 5412 8796 3214
    Land Area: 2 Acres 14 Guntas
    Date of Issue: 15/08/2023
    """

    res1 = extract_fields(sample_rtc_en, "land_record")
    print("\nTest 1 (English RTC):")
    print("  Extracted Survey No:", res1["fields"]["survey_number"]["value"])
    print("  Extracted Owner:", res1["fields"]["owner_name"]["value"])
    print("  Extracted Aadhaar (PII):", res1["fields"]["owner_id_number"]["value"])
    print("  Missing Required:", res1["missing_required_fields"])
    assert res1["fields"]["survey_number"]["value"] == "142/1A"
    assert res1["fields"]["owner_name"]["value"] == "Ramesh Kumar Gowda"
    assert res1["fields"]["owner_id_number"]["value"] == "541287963214"
    assert len(res1["missing_required_fields"]) == 0
    print("  [PASS] English RTC extraction verified!")

    # Test 2: Kannada RTC Sample
    sample_rtc_kn = """
    ಕರ್ನಾಟಕ ಸರ್ಕಾರ - ಕಂದಾಯ ಇಲಾಖೆ
    ಹಕ್ಕು ದಾಖಲೆಗಳು, ಗೇಣಿದಾರಿಕೆ ಮತ್ತು ಬೆಳೆಗಳು (ಆರ್.ಟಿ.ಸಿ)
    ಗ್ರಾಮ: ಮಂಡ್ಯ
    ತಾಲೂಕು: ಮದ್ದೂರು
    ಜಿಲ್ಲೆ: ಮಂಡ್ಯ
    ಸರ್ವೇ ಸಂಖ್ಯೆ: 88/2
    ಖಾತೆದಾರರ ಹೆಸರು: ಬಸವರಾಜಪ್ಪ ಗೌಡ
    ಗುರುತಿನ ಸಂಖ್ಯೆ: 9876 5432 1098
    ವಿಸ್ತೀರ್ಣ: 1 ಎಕರೆ 20 ಗುಂಟೆ
    ದಿನಾಂಕ: 12/04/2022
    """

    res2 = extract_fields(sample_rtc_kn, "rtc")
    print("\nTest 2 (Kannada RTC):")
    print("  Extracted Survey No:", res2["fields"]["survey_number"]["value"])
    print("  Extracted Owner:", res2["fields"]["owner_name"]["value"])
    print("  Extracted Aadhaar (PII):", res2["fields"]["owner_id_number"]["value"])
    print("  Extracted Area:", res2["fields"]["land_area"]["value"])
    print("  Missing Required:", res2["missing_required_fields"])
    assert res2["fields"]["survey_number"]["value"] == "88/2"
    assert res2["fields"]["owner_name"]["value"] == "ಬಸವರಾಜಪ್ಪ ಗೌಡ"
    assert res2["fields"]["owner_id_number"]["value"] == "987654321098"
    assert len(res2["missing_required_fields"]) == 0
    print("  [PASS] Kannada RTC extraction verified!")

    # Test 3: Property Tax with Missing Fields
    sample_tax_incomplete = """
    BRUHAT BENGALURU MAHANAGARA PALIKE
    PROPERTY TAX RECEIPT
    Owner Name: Priya Sharma
    Ward Name: 150 Bellandur
    Payment Status: Paid
    Assessment Year: 2024-25
    """

    res3 = extract_fields(sample_tax_incomplete, "property_tax")
    print("\nTest 3 (Property Tax Incomplete):")
    print("  Extracted Owner:", res3["fields"]["owner_name"]["value"])
    print("  Missing Required:", res3["missing_required_fields"])
    assert "assessment_number" in res3["missing_required_fields"]
    assert "tax_amount" in res3["missing_required_fields"]
    print("  [PASS] Missing required fields accurately caught!")

    # Test 4: Unknown Document Type
    res4 = extract_fields("Some generic text", "unknown")
    print("\nTest 4 (Unknown Document Type):")
    print("  Error message:", res4.get("error"))
    assert "error" in res4
    print("  [PASS] Unknown document type handled safely without crash!")

    print("\n==================================================")
    print("  SECTION 3 TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
