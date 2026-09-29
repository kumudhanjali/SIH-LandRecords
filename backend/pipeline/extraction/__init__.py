"""
Extraction package.
Provides field extractor and document schemas.
"""

from pipeline.extraction.field_extractor import extract_fields
from pipeline.extraction.schemas import DOCUMENT_SCHEMAS, get_schema_for_type

__all__ = ["extract_fields", "DOCUMENT_SCHEMAS", "get_schema_for_type"]
