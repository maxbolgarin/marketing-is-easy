# Marketing-is-Easy User Guide

## Overview

Marketing-is-Easy is a social marketing dashboard for creating, scheduling, and publishing content across multiple platforms: Telegram, Instagram, YouTube, Twitter. It supports AI-powered text, image, and video generation, organized by themes.

---

## Core Concepts

**Post** — A piece of content (text, image, video) that can be published to one or more platforms. Each post goes through a lifecycle: draft, generation, review, approval, and publishing.

**Theme** — A way to organize posts around a topic or campaign. Themes define target platforms, publishing cadence, and generation context. Posts can exist without a theme.

**Platform Variant** — A platform-specific version of a post with adapted text respecting character limits. Each post can have variants for different platforms.

**Publication** — A record of a post being published (or scheduled) to a specific platform.

---

## Getting Started

### Dashboard

The Dashboard shows a high-level overview:

- **Stats row** — Scheduled this week, pending review, published this month, failed count
- **Attention cards** — Quick links to posts needing review or that have failed
- **Next 48h timeline** — Scrollable view of upcoming scheduled posts
- **Active themes** — Progress of each active theme with published/total ratio

### Navigation

The sidebar provides access to all sections:
- **Dashboard** — Overview
- **Calendar** — Week view for scheduling
- **Themes** — Content theme management
- **Content Library** — Uploaded media assets
- **Channels** — Posts filtered by platform (Telegram, Instagram, YouTube, Twitter, Email)
- **Settings** — Account, connected channels, API configuration

---

## Creating a Post

### From the Calendar
1. Navigate to **Calendar**
2. Click the **"+"** button on any day column
3. The post editor opens automatically with a new draft

### From a Channel Page
1. Click any channel in the sidebar (e.g. Telegram)
2. Click **"New Post"** in the top right
3. The editor creates a draft and opens it

### From a Theme (Batch Generation)
1. Go to **Themes** and open a theme
2. Use batch generation to create multiple posts at once with the theme's context and target platforms

In all cases, a draft post is automatically created and the editor opens.

---

## Post Editor

The editor is a slide-over panel with four tabs:

### Content Tab

**Text** — Choose between two modes:
- **Static**: Write text manually in the textarea
- **Generated**: Enter a prompt describing what you want, then click **"Generate"**. The AI writes the text. You can edit the result manually after generation.

**Image** — Four options:
- **None**: No image
- **Upload**: Drag-and-drop or click to upload (PNG, JPG, WEBP, max 10 MB)
- **Generate**: Enter an image prompt and click **"Generate Image"**
- **Template**: Coming soon

**Video** — Three options:
- **None**: No video
- **Upload**: Upload a video file (MP4, MOV, max 500 MB)
- **Generate**: Click **"Generate Video"** to run the full pipeline (scene planning, image generation, motion clips, TTS narration, composition). This can take several minutes.

**Actions:**
- **Send to Review** — Moves the post to review status
- **Mark as Final** — Approves the post for publishing

### Platforms Tab

Shows platform variants for the post. Each variant card displays:
- Platform name and icon
- Platform-specific text (auto-adapted from the main content)
- Character count with limit indicator
- Enable/disable toggle
- Edit button to customize text per platform

**Character limits:**
| Platform | Limit |
|---|---|
| Telegram | 4,096 |
| Instagram | 2,200 |
| YouTube Short | 5,000 |
| Twitter | 280 |

Platform variants are created automatically when content is generated. You can also manually adjust text per platform.

### Schedule Tab

- Pick a date and time using the datetime picker
- Click **"Schedule"** to set the publication time
- Click **"Clear"** to remove the schedule
- Use **"Reschedule"** to change an existing time

Posts without a schedule can still be published manually.

### History Tab

Shows the post's history and metadata.

---

## Post Lifecycle

```
draft → generating → review → approved → publishing → published
                                  ↓                       ↓
                              rejected                  failed
```

1. **Draft** — Initial state. Edit content, add media, set prompts.
2. **Generating** — AI is creating content. The editor auto-refreshes every 3 seconds.
3. **Review** — Content ready for review. Click "Send to Review" to enter this state.
4. **Approved** — Click "Mark as Final". Post is queued for publishing.
5. **Publishing** — The publish worker is sending the post to platforms.
6. **Published** — Successfully sent to all enabled platforms.
7. **Failed** — Publishing error occurred. Check the error message in the Platforms tab.
8. **Rejected** — Post was rejected and can be reworked.

---

## Themes

Themes help organize posts by topic, campaign, or content series.

### Creating a Theme

1. Go to **Themes**
2. Click **"New Theme"**
3. Fill in the form:
   - **Name** (required) — e.g. "Weekly Tips", "Product Launch"
   - **Description** — What the theme is about
   - **Cadence** — Manual, Daily, or Weekly
   - **Target Platforms** — Select which platforms posts should target
   - **Color** — Pick a color for visual identification
4. Click **"Create Theme"**

### Theme Detail Page

Click a theme card to see its detail page:
- Theme info: status, description, platforms, cadence, progress
- List of all posts in the theme
- Each post shows: content preview, status, schedule time, platform icons
- Hover actions: preview, edit, generate

### Batch Generation

From a theme detail page, you can generate multiple posts at once. The generation uses the theme's context and targets the theme's platforms.

### Theme Statuses

- **Draft** — Theme is being set up
- **Active** — Theme is live and producing content
- **Paused** — Temporarily stopped
- **Completed** — Campaign finished

---

## Calendar

The Calendar page shows a week view of scheduled posts.

### Navigation
- Use **"<"** and **">"** arrows to move between weeks
- Click **"Today"** to jump to the current week
- Week range is displayed (e.g. "Mar 9 – 15, 2026")

### Filtering

Click the filter button to narrow the view by:
- **Theme** — Show posts from specific themes (with color dots)
- **Platform** — Show posts for specific platforms
- **Status** — Show posts with specific statuses

Active filter count is shown as a badge.

### Day Columns

Each day shows:
- Scheduled posts sorted by time
- Post cards with: time, status dot, text preview, platform icons, theme color accent
- Click a post card to open the editor
- Click the "+" area to create a new post on that day

---

## Channels

Channel pages show posts assigned to a specific platform.

### How Posts Appear in Channels

Posts appear in a channel when they have a **platform variant** for that platform:
1. Create or open a post
2. Go to the **Platforms** tab in the editor
3. Platform variants are created automatically during content generation
4. Enable/disable specific platforms using the toggle

### Each Channel Page Shows
- Platform icon and name
- All posts that have a variant for this platform
- "New Post" button to create a post directly

---

## Content Library

Upload and manage media assets:
- Click **"Upload"** or drag-and-drop files
- Supported: images (PNG, JPG, WEBP) and videos (MP4, MOV)
- Assets are displayed in a grid with thumbnails and file info
- Uploaded assets can be used in posts

---

## Settings

### Brand Profile
- View your username, email, account ID, and status

### Connected Accounts
- See all connected platform accounts
- **Test** connection for each account
- **Enable/disable** accounts with toggle switches
- View token expiration dates

### Configuration
- View and edit API keys and settings
- Settings grouped by category
- Source indicators: DB, ENV, or default
- Secrets are hidden by default (click to reveal)
