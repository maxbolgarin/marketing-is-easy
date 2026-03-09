"""Inline keyboards for the admin bot."""

from __future__ import annotations

import uuid

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def review_keyboard(post_id: uuid.UUID) -> InlineKeyboardMarkup:
    """Keyboard shown under a post preview for review."""
    pid = str(post_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve & Publish Now", callback_data=f"approve_now:{pid}"),
            ],
            [
                InlineKeyboardButton(text="📅 Schedule", callback_data=f"schedule:{pid}"),
                InlineKeyboardButton(text="🔄 Regenerate", callback_data=f"regenerate:{pid}"),
            ],
            [
                InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit:{pid}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{pid}"),
            ],
        ]
    )


def schedule_keyboard(post_id: uuid.UUID) -> InlineKeyboardMarkup:
    """Time slot selection after clicking Schedule."""
    pid = str(post_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⏰ In 1 hour", callback_data=f"sched_1h:{pid}"),
                InlineKeyboardButton(text="⏰ In 3 hours", callback_data=f"sched_3h:{pid}"),
            ],
            [
                InlineKeyboardButton(text="🌅 Tomorrow 9:00", callback_data=f"sched_tom9:{pid}"),
                InlineKeyboardButton(text="🌇 Tomorrow 18:00", callback_data=f"sched_tom18:{pid}"),
            ],
            [
                InlineKeyboardButton(text="🔙 Back", callback_data=f"back_review:{pid}"),
            ],
        ]
    )


def confirm_publish_keyboard(post_id: uuid.UUID) -> InlineKeyboardMarkup:
    """Confirm immediate publish."""
    pid = str(post_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes, publish now", callback_data=f"confirm_publish:{pid}"),
                InlineKeyboardButton(text="🔙 Back", callback_data=f"back_review:{pid}"),
            ],
        ]
    )


def media_type_keyboard(post_type: str) -> InlineKeyboardMarkup:
    """Select media type when generating a new post."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Text Only", callback_data=f"media_type:text:{post_type}"),
            ],
            [
                InlineKeyboardButton(text="🖼 AI Image", callback_data=f"media_type:ai:{post_type}"),
                InlineKeyboardButton(text="🎨 Branded Card", callback_data=f"media_type:card:{post_type}"),
            ],
            [
                InlineKeyboardButton(text="🎬 Video Short", callback_data=f"media_type:video:{post_type}"),
            ],
        ]
    )


def image_review_keyboard(post_id: uuid.UUID) -> InlineKeyboardMarkup:
    """Review keyboard for image posts — adds Regen Image option."""
    pid = str(post_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve & Publish Now", callback_data=f"approve_now:{pid}"),
            ],
            [
                InlineKeyboardButton(text="📅 Schedule", callback_data=f"schedule:{pid}"),
                InlineKeyboardButton(text="🔄 Regen Image", callback_data=f"regen_image:{pid}"),
            ],
            [
                InlineKeyboardButton(text="✏️ Edit Caption", callback_data=f"edit:{pid}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{pid}"),
            ],
        ]
    )


def post_type_keyboard() -> InlineKeyboardMarkup:
    """Select post type when generating new content."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💊 Supplement Spotlight", callback_data="gen:supplement_spotlight"),
                InlineKeyboardButton(text="💡 Educational Tip", callback_data="gen:educational_tip"),
            ],
            [
                InlineKeyboardButton(text="🧪 Myth Busting", callback_data="gen:myth_busting"),
                InlineKeyboardButton(text="📊 Research Highlight", callback_data="gen:research_highlight"),
            ],
            [
                InlineKeyboardButton(text="✍️ Free Topic", callback_data="gen:free_topic"),
            ],
        ]
    )


def video_review_keyboard(post_id: uuid.UUID) -> InlineKeyboardMarkup:
    """Review keyboard for video posts."""
    pid = str(post_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Approve & Publish Now", callback_data=f"approve_now:{pid}"),
            ],
            [
                InlineKeyboardButton(text="📅 Schedule", callback_data=f"schedule:{pid}"),
                InlineKeyboardButton(text="🔄 Regen Video", callback_data=f"regen_video:{pid}"),
            ],
            [
                InlineKeyboardButton(text="✏️ Edit Caption", callback_data=f"edit:{pid}"),
                InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{pid}"),
            ],
        ]
    )


def platforms_keyboard(post_id: uuid.UUID) -> InlineKeyboardMarkup:
    """Select which platforms to publish to."""
    pid = str(post_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📢 Telegram Channel", callback_data=f"plat_tg:{pid}"),
            ],
            [
                InlineKeyboardButton(text="📷 Instagram", callback_data=f"plat_ig:{pid}"),
            ],
            [
                InlineKeyboardButton(text="🎬 YouTube Short", callback_data=f"plat_yt:{pid}"),
            ],
        ]
    )
