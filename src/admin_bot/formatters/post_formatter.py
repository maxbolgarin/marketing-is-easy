"""Format post previews for the admin Telegram chat."""

from __future__ import annotations

from datetime import datetime

from src.db.models import Post


def format_post_preview(post: Post) -> str:
    """Format a post for admin review in Telegram.

    Uses HTML parse mode for the admin chat.
    """
    status_emoji = {
        "draft": "📝",
        "review": "👀",
        "approved": "✅",
        "publishing": "🚀",
        "published": "📢",
        "failed": "❌",
        "rejected": "🚫",
    }

    emoji = status_emoji.get(post.status, "❓")
    post_type = (post.post_type or "text").replace("_", " ").title()

    header = (
        f"{emoji} <b>Post Preview</b> — {post_type}\n"
        f"Status: <code>{post.status}</code> | "
        f"ID: <code>{str(post.id)[:8]}</code>\n"
    )

    if post.scheduled_at:
        header += f"📅 Scheduled: {post.scheduled_at.strftime('%Y-%m-%d %H:%M UTC')}\n"

    if post.text_model:
        header += f"🤖 Model: <code>{post.text_model}</code>\n"

    if post.media_type == "image":
        header += "🖼 <b>Image post</b>\n"
    elif post.media_type == "video":
        header += "🎬 <b>Video post</b>\n"

    header += "\n─────────────────────\n\n"

    # The actual post content (plain text preview)
    content = post.text_content or "(no content)"

    # Truncate for preview if very long
    if len(content) > 3000:
        content = content[:3000] + "\n\n... (truncated)"

    footer = "\n\n─────────────────────"

    return header + content + footer


def format_post_published(post: Post, platform: str, url: str | None = None) -> str:
    """Format a confirmation message after publishing."""
    parts = [f"📢 <b>Published!</b>"]
    parts.append(f"Platform: {platform}")
    if url:
        parts.append(f'Link: <a href="{url}">View post</a>')
    parts.append(f"Post ID: <code>{str(post.id)[:8]}</code>")
    return "\n".join(parts)


def format_post_list(posts: list[Post]) -> str:
    """Format a list of posts for the admin."""
    if not posts:
        return "No posts found."

    lines = ["<b>Recent Posts:</b>\n"]
    for p in posts:
        status_emoji = {"review": "👀", "approved": "✅", "published": "📢", "failed": "❌"}.get(
            p.status, "📝"
        )
        title = (p.text_content or "")[:60].replace("\n", " ")
        if len(p.text_content or "") > 60:
            title += "..."
        sched = ""
        if p.scheduled_at:
            sched = f" | 📅 {p.scheduled_at.strftime('%m/%d %H:%M')}"
        lines.append(f"{status_emoji} <code>{str(p.id)[:8]}</code> {title}{sched}")

    return "\n".join(lines)
