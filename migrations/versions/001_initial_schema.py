"""Initial schema — all tables.

Revision ID: 001
Revises:
Create Date: 2026-03-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- content_sources ---
    op.create_table(
        "content_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("title", sa.Text()),
        sa.Column("body", sa.Text()),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("language", sa.String(5), nullable=False, server_default="en"),
        sa.Column("track", sa.String(5), nullable=False, server_default="eu"),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- posts ---
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True)),
        sa.Column("track", sa.String(5), nullable=False),
        sa.Column("language", sa.String(5), nullable=False),
        sa.Column("post_type", sa.String(50), nullable=False, server_default="text"),
        sa.Column("text_content", sa.Text()),
        sa.Column("text_prompt", sa.Text()),
        sa.Column("text_model", sa.String(100)),
        sa.Column("media_type", sa.String(20)),
        sa.Column("media_urls", postgresql.ARRAY(sa.String())),
        sa.Column("media_metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True)),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("approved_by", sa.String(100)),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("review_message_id", sa.Integer()),
        sa.Column("review_chat_id", sa.Integer()),
        sa.Column("generation_params", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_posts_status", "posts", ["status"])
    op.create_index("idx_posts_track", "posts", ["track"])
    op.create_index(
        "idx_posts_scheduled",
        "posts",
        ["scheduled_at"],
        postgresql_where=sa.text("status = 'approved'"),
    )

    # --- post_publications ---
    op.create_table(
        "post_publications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("post_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("platform", sa.String(30), nullable=False),
        sa.Column("platform_text", sa.Text()),
        sa.Column("platform_media_url", sa.Text()),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending", index=True),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("platform_post_id", sa.String(200)),
        sa.Column("platform_url", sa.Text()),
        sa.Column("error_message", sa.Text()),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("manual_message_id", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
    )
    op.create_index("idx_publications_status", "post_publications", ["status"])

    # --- platform_accounts ---
    op.create_table(
        "platform_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("track", sa.String(5), nullable=False),
        sa.Column("platform", sa.String(30), nullable=False),
        sa.Column("account_name", sa.String(200)),
        sa.Column("credentials", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("token_expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # --- content_templates ---
    op.create_table(
        "content_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("track", sa.String(5), nullable=False),
        sa.Column("platform", sa.String(30), nullable=False),
        sa.Column("template_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("content_templates")
    op.drop_table("platform_accounts")
    op.drop_index("idx_publications_status", "post_publications")
    op.drop_table("post_publications")
    op.drop_index("idx_posts_scheduled", "posts")
    op.drop_index("idx_posts_track", "posts")
    op.drop_index("idx_posts_status", "posts")
    op.drop_table("posts")
    op.drop_table("content_sources")
