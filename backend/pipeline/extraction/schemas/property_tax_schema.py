"""
Schema definition for Property Tax Receipt / Assessment records.
Plain dictionary definition with format patterns and PII flags. No DB/ORM imports.
"""

PROPERTY_TAX_SCHEMA = {
    "assessment_number": {
        "type": "str",
        "required": True,
        "pattern": r"^[0-9A-Za-z/-]+$",
        "description": "Property tax assessment number / SAS application number"
    },
    "property_id": {
        "type": "str",
        "required": False,
        "pattern": r"^[0-9A-Za-z/-]+$",
        "description": "Unique property PID / E-Khata identifier"
    },
    "owner_name": {
        "type": "str",
        "required": True,
        "description": "Property owner / taxpayer name"
    },
    "owner_id_number": {
        "type": "str",
        "required": False,
        "pattern": r"^\d{12}$",
        "pii": True,
        "description": "12-digit UID/Aadhaar of the property owner"
    },
    "ward_name": {
        "type": "str",
        "required": False,
        "description": "Municipal ward number or ward name"
    },
    "tax_amount": {
        "type": "str",
        "required": True,
        "pattern": r"^[0-9,.]+$",
        "description": "Property tax paid or assessed amount"
    },
    "payment_status": {
        "type": "str",
        "required": False,
        "description": "Payment status (e.g., Paid, Pending)"
    },
    "assessment_year": {
        "type": "str",
        "required": False,
        "pattern": r"^\d{4}(-\d{2,4})?$",
        "description": "Assessment financial year (e.g., 2023-24 or 2024)"
    }
}
