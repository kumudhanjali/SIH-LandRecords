"""
Format Validation Checks
Validates field values against schema definitions, regex patterns, and data types.
"""

import re
from typing import Dict, Any, List
from datetime import datetime


def _get_val(fields: Dict[str, Any], key: str) -> Any:
    """Helper to extract value whether fields is dict of dicts or dict of primitives."""
    item = fields.get(key)
    if isinstance(item, dict):
        return item.get("value")
    return item


def check_format(fields: Dict[str, Any], schema: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Validate field formatting against schema rules.

    Contract:
    Returns list of {"field": str, "issue": str} for anything not matching schema pattern/type.
    """
    issues = []
    if not schema:
        return issues

    for field_name, field_def in schema.items():
        val = _get_val(fields, field_name)
        is_required = field_def.get("required", False)
        pattern = field_def.get("pattern")
        expected_type = field_def.get("type", "str")

        # 1. Required field check
        if is_required and (val is None or str(val).strip() == ""):
            issues.append({
                "field": field_name,
                "issue": f"Missing required field: '{field_name}'"
            })
            continue

        if val is None or str(val).strip() == "":
            continue

        val_str = str(val).strip()

        # 2. Regex pattern validation
        if pattern:
            if not re.match(pattern, val_str):
                issues.append({
                    "field": field_name,
                    "issue": f"Value '{val_str}' does not match required pattern '{pattern}'"
                })

        # 3. Date format validation
        if expected_type == "date":
            # Test common date representations
            date_parsed = False
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"):
                try:
                    datetime.strptime(val_str, fmt)
                    date_parsed = True
                    break
                except ValueError:
                    continue
            if not date_parsed:
                issues.append({
                    "field": field_name,
                    "issue": f"Invalid date format for '{val_str}'. Expected YYYY-MM-DD or DD/MM/YYYY."
                })

    return issues
