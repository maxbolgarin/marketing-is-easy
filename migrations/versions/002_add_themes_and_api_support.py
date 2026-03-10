"""Add themes, api_users, and posts.theme_id.

Revision ID: 002
Revises: 001
Create Date: 2026-03-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- themes ---
    op.create_table(
        "themes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("target_platforms", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("cadence_type", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("cadence_rule", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("start_date", sa.DateTime(timezone=True)),
        sa.Column("end_date", sa.DateTime(timezone=True)),
        sa.Column("generation_context", sa.Text()),
        sa.Column("default_prompt_template", sa.Text()),
        sa.Column("color", sa.String(20), nullable=False, server_default="#3B82F6"),
        sa.Column("template_id", postgresql.UUID(as_uuid=True)),
        sa.Column("track", sa.String(5), nullable=False, server_default="eu"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_themes_status", "themes", ["status"])

    # --- api_users ---
    op.create_table(
        "api_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(200)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- posts.theme_id ---
    op.add_column(
        "posts",
        sa.Column("theme_id", postgresql.UUID(as_uuid=True)),
    )
    op.create_foreign_key(
        "fk_posts_theme_id",
        "posts",
        "themes",
        ["theme_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("idx_posts_theme_id", "posts", ["theme_id"])


def downgrade() -> None:
    op.drop_index("idx_posts_theme_id", "posts")
    op.drop_constraint("fk_posts_theme_id", "posts", type_="foreignkey")
    op.drop_column("posts", "theme_id")
    op.drop_table("api_users")
    op.drop_index("idx_themes_status", "themes")
    op.drop_table("themes")
