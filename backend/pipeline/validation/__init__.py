"""
Validation package.
Aggregates format checks, logical consistency checks, and cross-record lookups.
"""

from typing import Dict, Any, List, Optional, Callable
from pipeline.validation.format_checks import check_format
from pipeline.validation.logical_checks import check_logic
from pipeline.validation.cross_record_checks import check_cross_record
from pipeline.extraction.schemas import get_schema_for_type


def validate_all(
    fields: Dict[str, Any],
    document_type: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    lookup_fn: Optional[Callable[[str], List[Dict[str, Any]]]] = None
) -> List[Dict[str, str]]:
    """
    Run complete validation suite (format, logical, and cross-record checks).
    Returns unified list of validation issue dicts: [{"field": str, "issue": str}, ...]
    """
    if schema is None and document_type:
        schema = get_schema_for_type(document_type)

    format_issues = check_format(fields, schema) if schema else []
    logical_issues = check_logic(fields)
    cross_issues = check_cross_record(fields, lookup_fn)

    # Combine all issues into single list
    return format_issues + logical_issues + cross_issues


__all__ = [
    "check_format",
    "check_logic",
    "check_cross_record",
    "validate_all"
]
