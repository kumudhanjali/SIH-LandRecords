"""
Schema definition for Registered Sale Deed documents.
Plain dictionary definition with format patterns and PII flags. No DB/ORM imports.
"""

SALE_DEED_SCHEMA = {
    "document_number": {
        "type": "str",
        "required": True,
        "pattern": r"^[0-9A-Za-z/-]+$",
        "description": "Registered document / deed registration number"
    },
    "seller_name": {
        "type": "str",
        "required": True,
        "description": "Full name of the seller / executant"
    },
    "seller_id_number": {
        "type": "str",
        "required": False,
        "pattern": r"^\d{12}$",
        "pii": True,
        "description": "12-digit UID/Aadhaar of the seller"
    },
    "buyer_name": {
        "type": "str",
        "required": True,
        "description": "Full name of the buyer / purchaser"
    },
    "buyer_id_number": {
        "type": "str",
        "required": False,
        "pattern": r"^\d{12}$",
        "pii": True,
        "description": "12-digit UID/Aadhaar of the buyer"
    },
    "survey_number": {
        "type": "str",
        "required": True,
        "pattern": r"^[0-9]+(/[0-9A-Za-z*-]+)?$",
        "description": "Survey number of the conveyed parcel"
    },
    "village": {
        "type": "str",
        "required": True,
        "description": "Village jurisdiction"
    },
    "district": {
        "type": "str",
        "required": True,
        "description": "Registration district"
    },
    "transaction_amount": {
        "type": "str",
        "required": False,
        "pattern": r"^[0-9,.]+$",
        "description": "Sale consideration amount in INR"
    },
    "execution_date": {
        "type": "date",
        "required": False,
        "description": "Date of deed execution / registration"
    }
}
