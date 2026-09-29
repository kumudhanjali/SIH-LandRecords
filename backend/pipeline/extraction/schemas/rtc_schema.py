"""
Schema definition for RTC / Pahani (Record of Rights, Tenancy and Crops).
Plain dictionary definition with format patterns and PII flags. No DB/ORM imports.
"""

RTC_SCHEMA = {
    "survey_number": {
        "type": "str",
        "required": True,
        "pattern": r"^[0-9]+(/[0-9A-Za-z*-]+)?$",
        "description": "Survey number of the land parcel (e.g. 142, 142/1, or 142/1A)"
    },
    "hissa_number": {
        "type": "str",
        "required": False,
        "pattern": r"^[0-9A-Za-z*]+$",
        "description": "Sub-division or Hissa number"
    },
    "owner_name": {
        "type": "str",
        "required": True,
        "description": "Full name of the land owner / occupant"
    },
    "owner_id_number": {
        "type": "str",
        "required": False,
        "pattern": r"^\d{12}$",
        "pii": True,
        "description": "Unique identifier of the owner (e.g., 12-digit Aadhaar)"
    },
    "village": {
        "type": "str",
        "required": True,
        "description": "Revenue village name"
    },
    "taluk": {
        "type": "str",
        "required": False,
        "description": "Taluk / Sub-district name"
    },
    "district": {
        "type": "str",
        "required": True,
        "description": "District name"
    },
    "land_area": {
        "type": "str",
        "required": True,
        "description": "Extent of land (e.g., 2 Acres 15 Guntas, or numeric area in hectares/sq ft)"
    },
    "document_date": {
        "type": "date",
        "required": False,
        "description": "Record issuance or reference date (YYYY-MM-DD or DD/MM/YYYY)"
    }
}
