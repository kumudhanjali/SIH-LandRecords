"""
Cross Record Validation Checks
Enables injectable database cross-record verification (e.g., verifying survey number against
registered ownership or checking for active encumbrances).
Degrades gracefully to a no-op when lookup_fn is None.
"""

from typing import Dict, Any, List, Optional, Callable


def _get_val(fields: Dict[str, Any], key: str) -> Any:
    """Helper to extract value whether fields is dict of dicts or dict of primitives."""
    item = fields.get(key)
    if isinstance(item, dict):
        return item.get("value")
    return item


def check_cross_record(
    fields: Dict[str, Any],
    lookup_fn: Optional[Callable[[str], List[Dict[str, Any]]]] = None
) -> List[Dict[str, str]]:
    """
    Perform cross-record validation with external database records.

    Contract:
    - lookup_fn: optional injectable callable(identifier: str) -> list[dict]
      Returns list of existing records matching survey_number or owner_id.
    - If lookup_fn is None: returns [] (no-op) immediately.
    - If lookup_fn returns records: verifies consistency (e.g., matching khatedar or flagged disputes).
    """
    # 1. Graceful no-op if no lookup function provided (DB not connected yet)
    if lookup_fn is None:
        return []

    issues = []
    survey_no = _get_val(fields, "survey_number")
    owner_id = _get_val(fields, "owner_id_number") or _get_val(fields, "new_owner_id")
    current_owner = _get_val(fields, "owner_name") or _get_val(fields, "new_owner")

    # 2. Check survey number in master registry
    if survey_no:
        try:
            records = lookup_fn(str(survey_no))
            if records:
                # Check for active legal disputes or court stay orders
                for rec in records:
                    if rec.get("status") == "disputed":
                        issues.append({
                            "field": "survey_number",
                            "issue": f"Survey number '{survey_no}' is marked under active dispute in registry: {rec.get('dispute_reason', 'Court stay')}"
                        })
                    if rec.get("is_government_land") is True:
                        issues.append({
                            "field": "survey_number",
                            "issue": f"Survey number '{survey_no}' is registered as Government/Gomal land."
                        })
        except Exception as e:
            issues.append({
                "field": "survey_number",
                "issue": f"Cross-record lookup failed: {str(e)}"
            })

    # 3. Check owner ID record consistency
    if owner_id:
        try:
            owner_records = lookup_fn(str(owner_id))
            if owner_records and current_owner:
                for rec in owner_records:
                    reg_name = rec.get("registered_name")
                    if reg_name and reg_name.lower().strip() != str(current_owner).lower().strip():
                        # Notice: potential mismatch warning
                        issues.append({
                            "field": "owner_name",
                            "issue": f"Owner name '{current_owner}' differs from name in UID registry ('{reg_name}')"
                        })
        except Exception as e:
            issues.append({
                "field": "owner_id_number",
                "issue": f"Cross-record owner lookup failed: {str(e)}"
            })

    return issues
