# BioMaxing Social Marketing Service

Automated social media content generation and publishing platform. Generates text posts, branded images, and short-form videos using AI, reviews them via a Telegram admin bot, and publishes to Telegram, Instagram, and YouTube.

**Stack:** Python 3.12, PostgreSQL, Redis, aiogram 3, OpenRouter, OpenAI API, Docker Compose

---

## Table of Contents

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Running in Docker](#running-in-docker)
- [Running Locally (Dev)](#running-locally-dev)
- [Configuration](#configuration)
- [Bot Commands](#bot-commands)
- [Content Generation](#content-generation)
- [Publishing](#publishing)
- [Video Pipeline](#video-pipeline)
- [Project Structure](#project-structure)
- [Cost Estimates](#cost-estimates)
- [Multi-Track Deployment](#multi-track-deployment)

---

## How It Works

1. **Generate** — Admin sends `/generate` in Telegram, picks a post type and topic, chooses a format (text, image, branded card, or video)
2. **Review** — The bot shows a preview with action buttons: approve, schedule, edit, regenerate, or reject
3. **Publish** — On approval, the post is published to Telegram channel + Instagram/YouTube (if configured). Scheduled posts are auto-published by a background worker

```
Admin Chat                   Background Workers              Platforms
──────────                   ──────────────────              ─────────
/generate                    generation-worker               Telegram Channel
  → post type                  → text via OpenRouter         Instagram
  → topic                     → images via OpenRouter        YouTube Shorts
  → format                    → branded cards via Pillow
      ↓                       → videos via OpenAI
  Review preview             publish-worker
  [Approve] [Schedule]         → scheduled post publishing
  [Edit] [Regenerate]       video-worker
  [Reject]                     → long-running video jobs
      ↓                     token-refresher
  Published                    → Instagram OAuth refresh
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     ADMIN BOT (aiogram 3)                    │
│  /generate → post type → topic → format → review → publish  │
│  /queue    → posts awaiting review                           │
│  /recent   → last 15 posts                                   │
└────────────────────────┬─────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────────┐
│   Content   │ │  Publishing  │ │     Workers       │
│   Engine    │ │   Engine     │ │                   │
│             │ │              │ │ generation-worker  │
│ Text Gen    │ │ Telegram     │ │ publish-worker     │
│ Image Gen   │ │ Instagram    │ │ video-worker       │
│ Image Comp  │ │ YouTube      │ │ token-refresher    │
│ Video Pipe  │ │ Manual       │ │                   │
└──────┬──────┘ └──────┬───────┘ └────────┬──────────┘
       │               │                  │
       └───────────────┼──────────────────┘
                       ▼
       ┌───────────────────────────────┐
       │          DATA LAYER           │
       │  PostgreSQL    │    Redis     │
       │  (posts, pubs, │  (task queue,│
       │   accounts)    │  video queue)│
       └───────────────────────────────┘
```

### Services

| Service | Command | Purpose |
|---------|---------|---------|
| `admin-bot` | `python -m src.admin_bot.bot` | Telegram bot for content management and review |
| `generation-worker` | `python -m src.workers.generation_worker` | Background text/image generation and regeneration |
| `video-worker` | `python -m src.workers.video_worker` | Dedicated long-running video generation (5–60 min per video) |
| `publish-worker` | `python -m src.workers.publish_worker` | Auto-publishes scheduled posts every 30 seconds |
| `token-refresher` | `python -m src.workers.token_refresh_worker` | Refreshes Instagram OAuth tokens (checks hourly, refreshes 10 days before expiry) |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose (for PostgreSQL and Redis)
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- An [OpenRouter](https://openrouter.ai/) API key (for text and image generation)
- An [OpenAI](https://platform.openai.com/) API key (for video pipeline — optional)
- FFmpeg (for video composition — installed automatically in Docker)

### 1. Clone and Configure

```bash
git clone <repo-url> && cd marketing-is-easy
cp .env.example .env
```

Edit `.env` with your tokens. At minimum you need:

```env
TG_BOT_TOKEN=your-bot-token
TG_ADMIN_CHAT_ID=your-chat-id
TG_CHANNEL_ID=your-channel-id
TG_ADMIN_USER_IDS=your-telegram-user-id
OPENROUTER_API_KEY=your-openrouter-key
```

### 2. Download Fonts (for branded image cards)

```bash
python scripts/download_fonts.py
```

This downloads Roboto Regular and Bold to `templates/fonts/`.

---

## Running in Docker

The simplest way to run everything:

```bash
docker compose up --build
```

This starts all 7 services: PostgreSQL, Redis, admin-bot, generation-worker, publish-worker, video-worker, and token-refresher.

The database tables are created automatically on first startup.

To run only core services (without video):

```bash
docker compose up postgres redis admin-bot generation-worker publish-worker
```

---

## Running Locally (Dev)

### 1. Start Infrastructure

```bash
docker compose up -d postgres redis
```

### 2. Install Dependencies

```bash
pip install -e ".[dev]"
# or
pip install -r requirements.txt
```

For video support, also install FFmpeg:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start Services

Open separate terminals:

```bash
# Terminal 1: Admin bot
python -m src.admin_bot.bot

# Terminal 2: Generation worker (text/image regeneration)
python -m src.workers.generation_worker

# Terminal 3: Publish worker (scheduled publishing)
python -m src.workers.publish_worker

# Terminal 4: Video worker (optional — only needed for video generation)
python -m src.workers.video_worker

# Terminal 5: Token refresher (optional — only needed for Instagram)
python -m src.workers.token_refresh_worker
```

### 5. Test It

Open your Telegram admin chat and send `/generate`. Follow the prompts to create your first post.

---

## Configuration

All configuration is via environment variables (see `.env.example` for the full list).

### Required (Phase 1 — Text + Telegram)

| Variable | Description |
|----------|-------------|
| `TG_BOT_TOKEN` | Telegram bot token from @BotFather |
| `TG_ADMIN_CHAT_ID` | Chat ID where you review posts |
| `TG_CHANNEL_ID` | Target Telegram channel ID |
| `TG_ADMIN_USER_IDS` | Comma-separated Telegram user IDs with admin access |
| `OPENROUTER_API_KEY` | OpenRouter API key for text/image generation |

### Image + Instagram (Phase 2)

| Variable | Description |
|----------|-------------|
| `MEDIA_BASE_URL` | Public URL where media files are served (**required for Instagram**) |
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived Instagram access token (60-day, auto-refreshed) |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram Business account ID |

Instagram requires images at public URLs. Point `MEDIA_BASE_URL` to a server that serves the `MEDIA_STORAGE_PATH` directory:

```nginx
# Example nginx config
location /media/ {
    alias /app/media/;
}
```

### Video + YouTube (Phase 3)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key (for sora-2, gpt-image-1-mini, TTS, Whisper) |
| `YOUTUBE_CLIENT_ID` | Google Cloud OAuth 2.0 client ID |
| `YOUTUBE_CLIENT_SECRET` | Google Cloud OAuth 2.0 client secret |
| `YOUTUBE_REFRESH_TOKEN` | Obtained via `scripts/setup_oauth.py` |
| `VIDEO_ENABLE_MOTION` | Set to `false` for still-image-only videos (no sora-2 costs) |

### Video Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `VIDEO_FINAL_TARGET_SECONDS` | `36` | Target video duration |
| `VIDEO_MOTION_SCENE_COUNT` | `3` | Number of AI motion clips |
| `VIDEO_STILL_SCENE_COUNT` | `2` | Number of still-image scenes |
| `VIDEO_FPS` | `30` | Output framerate |
| `VIDEO_ENABLE_MOTION` | `true` | `false` = skip sora-2, use only still images |
| `BGM_PATH` | (empty) | Path to background music .wav file |
| `BGM_VOLUME` | `0.10` | Background music volume (0.0–1.0) |

### Brand Customization

| Variable | Default | Description |
|----------|---------|-------------|
| `BRAND_NAME` | `BioMaxing` | Brand name shown on slides and in prompts |
| `BRAND_HEADING_FONT` | (empty) | Path to heading .ttf font |
| `BRAND_BODY_FONT` | (empty) | Path to body .ttf font |
| `BRAND_LOGO_PATH` | (empty) | Path to logo .png |
| `BRAND_PRIMARY_TEAL` | `#53D7FF` | Primary accent color |
| `BRAND_BG` | `#06141A` | Dark background color |
| `BRAND_TEXT_COLOR` | `#F5FBFF` | Light text color |
| `CONTENT_TONE` | `scientific_casual` | LLM tone: `scientific_casual` or `accessible_preventive` |

### Getting Telegram IDs

- **Your user ID:** Message [@userinfobot](https://t.me/userinfobot) on Telegram
- **Channel ID:** Forward a channel message to @userinfobot, or use `https://api.telegram.org/bot<TOKEN>/getUpdates`
- **Admin chat ID:** Create a group, add your bot, send a message, check the getUpdates response

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with available commands |
| `/help` | Same as /start |
| `/generate` | Start content generation flow |
| `/queue` | Show posts awaiting review |
| `/recent` | Show last 15 posts |
| `/cancel` | Cancel current operation (during generation flow) |

---

## Content Generation

### Post Types

| Type | Inline Button | Description |
|------|---------------|-------------|
| Supplement Spotlight | 💊 | Deep-dive on a supplement (dosage, evidence, who benefits) |
| Educational Tip | 💡 | One actionable wellness/biohacking tip |
| Myth Busting | 🧪 | Debunk a health misconception with evidence |
| Research Highlight | 📊 | Summarize an interesting study finding |
| Free Topic | ✍️ | Any topic with custom instructions |

### Media Formats

| Format | Button | Generation Time | What Happens |
|--------|--------|-----------------|--------------|
| Text Only | 📝 | ~5–10s | LLM generates text → instant review |
| AI Image | 🖼 | ~15–30s | LLM text + OpenRouter image → review |
| Branded Card | 🎨 | ~15–30s | LLM text + Pillow rendered card (1080x1080) → review |
| Video Short | 🎬 | 5–30 min | LLM text + async video pipeline → notified when ready |

### Review Flow

After generation, the admin sees a preview with these options:

**Text posts:**
- ✅ Approve & Publish Now → publishes to Telegram
- 📅 Schedule → pick time slot (1h, 3h, tomorrow 9:00, tomorrow 18:00)
- ✏️ Edit → send replacement text
- 🔄 Regenerate → re-run LLM with higher temperature
- ❌ Reject → archived

**Image posts** — same as above, plus:
- 🔄 Regen Image → regenerate only the image

**Video posts** — same as above, plus:
- 🔄 Regen Video → re-run the full video pipeline

### Post Status Flow

```
draft → review → approved → publishing → published
                    ↓                        ↓
                 rejected                  failed
```

Scheduled posts sit at `approved` until their `scheduled_at` time, then the publish-worker picks them up.

---

## Publishing

### Telegram

Always available. Publishes text, photos, and videos to the configured channel. No special setup beyond the bot token and channel ID.

### Instagram

Publishes photos via the Meta Graph API v22. Requires a Facebook Business account linked to an Instagram Business/Creator account.

**Setup:**
1. Create a Facebook App with Instagram Graph API permissions
2. Generate a long-lived access token (60 days)
3. Set `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_BUSINESS_ACCOUNT_ID`
4. Serve media files at a public URL (`MEDIA_BASE_URL`)

The token-refresher worker auto-refreshes tokens 10 days before expiry.

**Fallback:** If Instagram publishing fails or `MEDIA_BASE_URL` is not set, the bot sends the post to your admin chat with copy-paste instructions and a "Mark as Posted" button.

### YouTube Shorts

Publishes videos via YouTube Data API v3. Requires Google Cloud OAuth 2.0 credentials.

**Setup:**
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Run `scripts/setup_oauth.py` to obtain a refresh token
3. Set `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`

Videos are auto-detected as Shorts by YouTube (9:16 aspect ratio, ≤60s duration). The `#Shorts` tag is added automatically to the description.

---

## Video Pipeline

The video pipeline transforms text content into polished 30–60 second vertical shorts. It runs as a dedicated background worker because generation can take 5–60 minutes.

### Pipeline Stages

```
[1] Plan       → LLM creates 6-scene script with visual prompts (gpt-5-mini)
[2] Visuals    → AI generates scene images (gpt-image-1-mini) + Pillow renders branded slides
[3] Motion     → AI generates motion clips for 3 scenes (sora-2) — skipped if VIDEO_ENABLE_MOTION=false
[4] Voiceover  → TTS generates narration audio (gpt-4o-mini-tts)
[5] Subtitles  → STT transcribes voiceover to SRT (whisper-1)
[6] Compose    → MoviePy assembles scenes + audio + captions into final 1080x1920 MP4
```

### Scene Structure

Each video has exactly 6 scenes:
- **3 motion clips** — AI-generated video (4, 8, or 12 seconds each)
- **2 still scenes** — AI-generated images with local animation
- **1 CTA slide** — Call-to-action outro

### Output

Each video run creates a directory under `/app/media/{track}/{YYYY/MM}/video/{timestamp}/`:

```
{run_dir}/
├── plan.json              # AI-generated script and scene breakdown
├── images/                # Raw AI-generated images per scene
├── rendered_slides/       # Branded slides with text overlay
├── clips/                 # Motion video clips (if enabled)
├── audio/voiceover.wav    # TTS narration
├── subtitles/subtitles.srt
└── final/
    ├── short.mp4          # Final 1080x1920 video
    ├── cover.jpg          # Cover frame
    └── caption.txt        # Social media caption
```

### Cheap Mode

Set `VIDEO_ENABLE_MOTION=false` to skip sora-2 motion generation entirely. The pipeline will use still images with branded overlays for all scenes, dramatically reducing cost (from ~$2–5 to ~$0.20 per video).

---

## Project Structure

```
marketing-is-easy/
├── src/
│   ├── config/
│   │   └── settings.py                  # Pydantic BaseSettings (all env vars)
│   ├── db/
│   │   ├── models.py                    # SQLAlchemy models (Post, PostPublication, etc.)
│   │   └── repo.py                      # Repository classes (PostRepo, PublicationRepo)
│   ├── content_engine/
│   │   ├── generators/
│   │   │   ├── text_generator.py        # OpenRouter text generation
│   │   │   ├── image_generator.py       # OpenRouter image generation
│   │   │   ├── image_composer.py        # Pillow branded cards (tip, quote, fact)
│   │   │   ├── platform_adapter.py      # Platform-specific text formatting
│   │   │   └── video/                   # Video pipeline package
│   │   │       ├── pipeline.py          # Async orchestrator
│   │   │       ├── planning.py          # LLM script generation
│   │   │       ├── visuals.py           # Scene image + branded slide generation
│   │   │       ├── video_clips.py       # Motion video generation (sora-2)
│   │   │       ├── tts.py              # Text-to-speech voiceover
│   │   │       ├── stt.py              # Speech-to-text subtitles
│   │   │       ├── compose.py           # MoviePy final assembly
│   │   │       ├── schemas.py           # Video data models
│   │   │       ├── openai_client.py     # OpenAI API client
│   │   │       └── utils.py            # Video pipeline helpers
│   │   └── prompts/
│   │       └── post_prompts.py          # LLM prompt templates per post type
│   ├── publishing/
│   │   ├── telegram_publisher.py        # Telegram channel publishing
│   │   ├── instagram_publisher.py       # Meta Graph API publishing
│   │   ├── youtube_publisher.py         # YouTube Data API v3 publishing
│   │   ├── manual_publisher.py          # Admin chat fallback for manual posting
│   │   └── token_manager.py            # Instagram OAuth token refresh
│   ├── admin_bot/
│   │   ├── bot.py                       # Bot entry point, router setup
│   │   ├── handlers/
│   │   │   ├── generate.py             # /generate flow (FSM states)
│   │   │   └── review.py              # Review, approve, schedule, publish
│   │   ├── keyboards/
│   │   │   └── inline.py              # Inline keyboard definitions
│   │   └── formatters/
│   │       └── post_formatter.py       # Post preview formatting
│   └── workers/
│       ├── generation_worker.py         # Text/image/video generation tasks
│       ├── publish_worker.py            # Scheduled post publishing
│       ├── video_worker.py              # Dedicated video generation worker
│       ├── token_refresh_worker.py      # OAuth token refresh
│       └── task_queue.py               # Redis task queues (main + video)
├── migrations/
│   └── versions/
│       └── 001_initial_schema.py       # Database schema
├── templates/
│   └── fonts/                          # Roboto fonts (downloaded via script)
├── scripts/
│   └── download_fonts.py              # Download Roboto fonts from Google
├── docker-compose.yml                  # 7 services: postgres, redis, bot, 4 workers
├── Dockerfile                          # Python 3.12 + ffmpeg
├── .env.example                        # All environment variables documented
├── pyproject.toml                      # Project config and dependencies
├── requirements.txt                    # Pinned dependencies
└── alembic.ini                         # Alembic migration config
```

---

## Cost Estimates

| Content Type | AI Cost per Post | Notes |
|-------------|-----------------|-------|
| Text only (Telegram) | $0.002–0.01 | OpenRouter LLM only |
| Image post (Instagram) | $0.02–0.20 | LLM text + AI image |
| Branded card (Instagram) | $0.002–0.01 | LLM text + local Pillow rendering |
| Video short (30s, cheap mode) | ~$0.20 | LLM + images + TTS + STT (no sora-2) |
| Video short (30s, full) | $1.00–3.00 | LLM + images + 3 sora-2 clips + TTS + STT |
| Video short (60s, full) | $2.00–5.00 | Same pipeline, more scenes |

**Monthly estimate (5 posts/week):**
- Text + image mix: ~$5–20/month
- With video (2 videos/week, full mode): ~$30–60/month additional

---

## Multi-Track Deployment

The service supports multiple brand tracks from the same codebase. Each track runs as a separate Docker Compose deployment with its own `.env` file.

| Setting | EU Track (BioMaxing) | RU Track (Vitabi) |
|---------|---------------------|-------------------|
| `TRACK` | `eu` | `ru` |
| `LANGUAGE` | `en` | `ru` |
| `BRAND_NAME` | `BioMaxing` | `Vitabi` |
| `CONTENT_TONE` | `scientific_casual` | `accessible_preventive` |

Each track has its own Telegram bot, channel, Instagram account, and YouTube channel. Content is stored in the same database but separated by the `track` column.

---

## Database Schema

5 tables managed via Alembic migrations:

- **posts** — Core content entity with status tracking, media URLs, generation params
- **post_publications** — Per-platform publish records (telegram, instagram_post, youtube_short)
- **content_sources** — Input data for content generation (articles, supplements, manual)
- **platform_accounts** — OAuth credentials and token expiry tracking
- **content_templates** — Reusable content/image templates

Tables are auto-created on first startup in dev mode. For production, use:

```bash
alembic upgrade head
```

---

## Troubleshooting

**Bot doesn't respond to commands:**
- Verify `TG_BOT_TOKEN` is correct
- Verify your Telegram user ID is in `TG_ADMIN_USER_IDS`
- Check bot logs: `docker compose logs admin-bot`

**Images not publishing to Instagram:**
- Instagram requires `MEDIA_BASE_URL` pointing to publicly accessible media files
- Check that `INSTAGRAM_ACCESS_TOKEN` is valid (tokens expire after 60 days)
- The token-refresher auto-renews tokens 10 days before expiry

**Video generation takes too long:**
- sora-2 motion clips can take 5–60 minutes per scene
- Set `VIDEO_ENABLE_MOTION=false` for instant still-image videos
- Check video-worker logs: `docker compose logs video-worker`

**Scheduled posts not publishing:**
- Ensure `publish-worker` is running
- It checks every 30 seconds for posts where `status=approved` and `scheduled_at <= now`
