"""
Schema definition for Land Mutation / Katha Transfer Orders.
Plain dictionary definition with format patterns and PII flags. No DB/ORM imports.
"""

MUTATION_SCHEMA = {
    "mutation_number": {
        "type": "str",
        "required": True,
        "pattern": r"^[0-9A-Za-z/-]+$",
        "description": "Mutation order number / MR number"
    },
    "survey_number": {
        "type": "str",
        "required": True,
        "pattern": r"^[0-9]+(/[0-9A-Za-z*-]+)?$",
        "description": "Survey number of the mutated land parcel"
    },
    "previous_owner": {
        "type": "str",
        "required": True,
        "description": "Name of the previous khatedar / transferor"
    },
    "new_owner": {
        "type": "str",
        "required": True,
        "description": "Name of the new khatedar / transferee"
    },
    "new_owner_id": {
        "type": "str",
        "required": False,
        "pattern": r"^\d{12}$",
        "pii": True,
        "description": "12-digit UID/Aadhaar of the new khatedar"
    },
    "mutation_type": {
        "type": "str",
        "required": False,
        "description": "Type of mutation (e.g., Sale, Inheritance/Varas, Gift, Partition)"
    },
    "village": {
        "type": "str",
        "required": True,
        "description": "Village name"
    },
    "district": {
        "type": "str",
        "required": True,
        "description": "District name"
    },
    "order_date": {
        "type": "date",
        "required": False,
        "description": "Date of mutation approval order"
    }
}
