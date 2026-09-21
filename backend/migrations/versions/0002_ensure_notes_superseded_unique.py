"""ensure notes.superseded_by_id is unique

The production database predates Alembic: its notes.superseded_by_id column was
added by hand without the UNIQUE constraint the model declares. Fresh databases
already get the constraint from 0001, so this only adds it when it is missing.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-21
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'notes_superseded_by_id_key'
            ) THEN
                ALTER TABLE notes
                    ADD CONSTRAINT notes_superseded_by_id_key UNIQUE (superseded_by_id);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # 0001 owns the constraint on fresh databases, so there is nothing to undo.
    pass
