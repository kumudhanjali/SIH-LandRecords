"""
Section 5 Standalone Test: Validation Module
Tests:
1. check_format: Validates patterns and types against schemas
2. check_logic: Catches future dates, non-positive amounts, identical seller/buyer
3. check_cross_record:
   - lookup_fn=None -> returns [] gracefully
   - mock lookup_fn -> catches disputed land
4. validate_all: Full aggregate execution
"""

import sys
import os
from datetime import date, timedelta

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.validation import check_format, check_logic, check_cross_record, validate_all
from pipeline.extraction.schemas import RTC_SCHEMA, SALE_DEED_SCHEMA


def run_tests():
    print("==================================================")
    print("  SECTION 5: VALIDATION MODULE TEST")
    print("==================================================")

    # Test 1: Clean valid fields
    valid_rtc = {
        "survey_number": {"value": "142/1"},
        "owner_name": {"value": "Ramesh Kumar"},
        "owner_id_number": {"value": "541287963214"},
        "village": {"value": "Ramanagara"},
        "district": {"value": "Ramanagara"},
        "land_area": {"value": "2 Acres 10 Guntas"},
        "document_date": {"value": "2023-05-12"}
    }
    format_issues_clean = check_format(valid_rtc, RTC_SCHEMA)
    logic_issues_clean = check_logic(valid_rtc)
    cross_issues_none = check_cross_record(valid_rtc, lookup_fn=None)
    all_clean = validate_all(valid_rtc, schema=RTC_SCHEMA, lookup_fn=None)

    print("\nTest 1 (Valid Data):")
    print(f"  Format issues: {len(format_issues_clean)}, Logic issues: {len(logic_issues_clean)}, Cross-record: {len(cross_issues_none)}")
    assert len(format_issues_clean) == 0
    assert len(logic_issues_clean) == 0
    assert len(cross_issues_none) == 0
    assert len(all_clean) == 0
    print("  [PASS] Clean valid record produces 0 validation issues.")

    # Test 2: Intentionally broken format data
    broken_rtc = {
        "survey_number": {"value": "INVALID#SURVEY*&"},
        "owner_name": {"value": ""},  # Missing required
        "owner_id_number": {"value": "12345"},  # Not 12 digits
        "village": {"value": "Ramanagara"},
        "district": {"value": "Ramanagara"},
        "land_area": {"value": "2 Acres"},
        "document_date": {"value": "NOT_A_DATE_VALUE"}
    }
    format_issues = check_format(broken_rtc, RTC_SCHEMA)
    print("\nTest 2 (Format Issues Detected):")
    for iss in format_issues:
        print(f"  - [{iss['field']}]: {iss['issue']}")
    assert any(i["field"] == "survey_number" for i in format_issues)
    assert any(i["field"] == "owner_name" for i in format_issues)
    assert any(i["field"] == "owner_id_number" for i in format_issues)
    assert any(i["field"] == "document_date" for i in format_issues)
    print("  [PASS] All format anomalies detected accurately.")

    # Test 3: Logical consistency issues
    future_date = (date.today() + timedelta(days=365)).isoformat()
    broken_deed = {
        "seller_name": {"value": "Anand Rao"},
        "buyer_name": {"value": "Anand Rao"},  # Same as seller
        "execution_date": {"value": future_date},  # Future date
        "transaction_amount": {"value": "-50000"}  # Negative amount
    }
    logic_issues = check_logic(broken_deed)
    print("\nTest 3 (Logic Issues Detected):")
    for iss in logic_issues:
        print(f"  - [{iss['field']}]: {iss['issue']}")
    assert any(i["field"] == "execution_date" for i in logic_issues)
    assert any(i["field"] == "buyer_name" for i in logic_issues)
    assert any(i["field"] == "transaction_amount" for i in logic_issues)
    print("  [PASS] All logical conflicts detected accurately.")

    # Test 4: Cross-record validation with mock lookup_fn
    def mock_db_lookup(key: str):
        if key == "142/1":
            return [{"status": "disputed", "dispute_reason": "High Court Stay Order OS/2023"}]
        return []

    cross_issues_mock = check_cross_record(valid_rtc, lookup_fn=mock_db_lookup)
    print("\nTest 4 (Cross-Record DB Lookup):")
    for iss in cross_issues_mock:
        print(f"  - [{iss['field']}]: {iss['issue']}")
    assert len(cross_issues_mock) == 1
    assert "dispute" in cross_issues_mock[0]["issue"].lower()
    print("  [PASS] Injectable cross-record check successfully flags disputed survey number.")

    print("\n==================================================")
    print("  SECTION 5 TESTS PASSED SUCCESSFULLY!")
    print("==================================================")


if __name__ == "__main__":
    run_tests()
