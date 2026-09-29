"""Create land record persistence tables."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    status = sa.Enum("pending", "auto_approved", "needs_review", "verified", name="document_status")
    op.create_table("documents",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("original_storage_path", sa.String(2048)), sa.Column("processed_storage_path", sa.String(2048)),
        sa.Column("document_type", sa.String(100)), sa.Column("language_detected", sa.String(50)),
        sa.Column("upload_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", status, server_default="pending", nullable=False), sa.Column("overall_confidence", sa.Float()))
    op.create_table("owners", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id_number_encrypted", sa.String(512), nullable=False, unique=True),
        sa.Column("owner_id_number_lookup_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(300), nullable=False), sa.Column("contact_info", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("properties", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("survey_number", sa.String(100), nullable=False), sa.Column("village", sa.String(200), nullable=False),
        sa.Column("taluk", sa.String(200)), sa.Column("district", sa.String(200), nullable=False),
        sa.Column("land_area", sa.String(200)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_properties_survey_number", "properties", ["survey_number"])
    op.create_table("extracted_fields", sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_name", sa.String(150), nullable=False), sa.Column("value", sa.Text()), sa.Column("raw_match", sa.Text()),
        sa.Column("confidence", sa.Float()), sa.Column("is_pii", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("verified_by", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("verified_at", sa.DateTime(timezone=True)),
        sa.Column("original_value", sa.Text()))
    op.create_index("ix_extracted_fields_document_id", "extracted_fields", ["document_id"])
    op.create_table("owner_property", sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("owners.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("relationship_type", sa.String(50), nullable=False))

def downgrade():
    op.drop_table("owner_property")
    op.drop_index("ix_extracted_fields_document_id", table_name="extracted_fields")
    op.drop_table("extracted_fields")
    op.drop_index("ix_properties_survey_number", table_name="properties")
    op.drop_table("properties")
    op.drop_table("owners")
    op.drop_table("documents")
    sa.Enum(name="document_status").drop(op.get_bind(), checkfirst=True)
