"""
Schemas package aggregating document extraction schemas.
Provides lookup dictionary for document types.
"""

from pipeline.extraction.schemas.rtc_schema import RTC_SCHEMA
from pipeline.extraction.schemas.sale_deed_schema import SALE_DEED_SCHEMA
from pipeline.extraction.schemas.mutation_schema import MUTATION_SCHEMA
from pipeline.extraction.schemas.property_tax_schema import PROPERTY_TAX_SCHEMA

# Schema mapping keyed by document types (including alias normalizations)
DOCUMENT_SCHEMAS = {
    "rtc": RTC_SCHEMA,
    "land_record": RTC_SCHEMA,
    "pahani": RTC_SCHEMA,
    "sale_deed": SALE_DEED_SCHEMA,
    "deed": SALE_DEED_SCHEMA,
    "mutation": MUTATION_SCHEMA,
    "mutation_record": MUTATION_SCHEMA,
    "property_tax": PROPERTY_TAX_SCHEMA,
    "tax_receipt": PROPERTY_TAX_SCHEMA,
}


def get_schema_for_type(document_type: str):
    """
    Look up schema by document type string.
    Returns schema dictionary or None if unknown.
    """
    if not document_type:
        return None
    normalized_key = document_type.strip().lower().replace(" ", "_")
    return DOCUMENT_SCHEMAS.get(normalized_key)


__all__ = [
    "RTC_SCHEMA",
    "SALE_DEED_SCHEMA",
    "MUTATION_SCHEMA",
    "PROPERTY_TAX_SCHEMA",
    "DOCUMENT_SCHEMAS",
    "get_schema_for_type",
]
