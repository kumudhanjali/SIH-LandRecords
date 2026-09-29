# Database setup

Install the backend requirements, then configure `DATABASE_URL` and `PII_ENCRYPTION_KEY` in the environment or `backend/.env` (the file is ignored by Git).

```env
DATABASE_URL=postgresql+psycopg://<user>:<password>@<host>:5432/<database>
PII_ENCRYPTION_KEY=<Fernet key>
```

Generate a Fernet key with:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Back up the encryption key securely. Existing PII ciphertext cannot be decrypted without the same key. Apply the schema from `backend` with `alembic upgrade head`. The separately managed `users` table, with an integer `id` column, must exist first for the `extracted_fields.verified_by` foreign key.

`python scripts/check_pipeline_persistence.py` writes a dummy document and checks the stored PII ciphertext directly. Run it only against a development database. Status policy is: missing confidence stays `pending`; confidence at least `0.90` with no validation issues becomes `auto_approved`; all other scored documents become `needs_review`.
