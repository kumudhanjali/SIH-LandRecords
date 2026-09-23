"""
Logical Validation Checks
Validates internal semantic consistency of extracted document fields.
Checks for future dates, non-positive areas/amounts, and party conflicts.
"""

import re
from typing import Dict, Any, List
from datetime import datetime, date


def _get_val(fields: Dict[str, Any], key: str) -> Any:
    """Helper to extract value whether fields is dict of dicts or dict of primitives."""
    item = fields.get(key)
    if isinstance(item, dict):
        return item.get("value")
    return item


def _parse_date(val_str: str) -> date | None:
    """Attempt to parse date string into date object."""
    if not val_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(val_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def check_logic(fields: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Perform internal logical consistency checks on fields.

    Contract:
    Returns list of {"field": str, "issue": str} for logical inconsistencies:
    - Dates occurring in the future
    - Zero or negative numeric land area or consideration amount
    - Identical buyer and seller names in conveyance deeds
    """
    issues = []
    today = date.today()

    # 1. Date consistency: Dates must not be in the future
    date_fields = ["document_date", "execution_date", "order_date"]
    for d_field in date_fields:
        val = _get_val(fields, d_field)
        if val:
            parsed = _parse_date(str(val))
            if parsed and parsed > today:
                issues.append({
                    "field": d_field,
                    "issue": f"Document date '{val}' cannot be in the future (today is {today.isoformat()})"
                })

    # 2. Land area sanity check
    area_val = _get_val(fields, "land_area")
    if area_val:
        # Extract numeric components
        nums = re.findall(r"\d+(?:\.\d+)?", str(area_val))
        if nums:
            total_num = sum(float(n) for n in nums)
            if total_num <= 0:
                issues.append({
                    "field": "land_area",
                    "issue": f"Land area '{area_val}' must represent a positive quantity."
                })

    # 3. Transaction Amount / Tax Amount positivity check
    for amt_field in ["transaction_amount", "tax_amount"]:
        amt_val = _get_val(fields, amt_field)
        if amt_val is not None:
            val_str = str(amt_val).strip()
            # Match number including optional leading minus
            match = re.search(r"-?\d+(?:\.\d+)?", val_str)
            if match:
                try:
                    numeric_val = float(match.group(0))
                    if numeric_val <= 0:
                        issues.append({
                            "field": amt_field,
                            "issue": f"{amt_field} '{amt_val}' must be a positive amount."
                        })
                except ValueError:
                    pass

    # 4. Buyer vs Seller identity conflict in Sale Deeds
    seller = _get_val(fields, "seller_name")
    buyer = _get_val(fields, "buyer_name")
    if seller and buyer and seller.strip().lower() == buyer.strip().lower():
        issues.append({
            "field": "buyer_name",
            "issue": f"Seller name and Buyer name cannot be identical ('{seller}')"
        })

    # 5. Previous owner vs New owner conflict in Mutation records
    prev_owner = _get_val(fields, "previous_owner")
    new_owner = _get_val(fields, "new_owner")
    if prev_owner and new_owner and prev_owner.strip().lower() == new_owner.strip().lower():
        issues.append({
            "field": "new_owner",
            "issue": f"Previous owner and New owner cannot be identical in mutation order ('{new_owner}')"
        })

    return issues
