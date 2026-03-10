# BioMaxing Social Marketing Service

Automated social media content generation and publishing platform. Generates text posts, branded images, and short-form videos using AI, reviews them via a Telegram admin bot or web dashboard, and publishes to Telegram, Instagram, and YouTube.

**Stack:** Python 3.12, FastAPI, PostgreSQL, Redis, React 19, TypeScript, Tailwind CSS, aiogram 3, OpenRouter, OpenAI API, Docker Compose

---

## Table of Contents

- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Running in Docker](#running-in-docker)
- [Running Locally (Dev)](#running-locally-dev)
- [Running on a VM](#running-on-a-vm)
- [Web Dashboard](#web-dashboard)
- [Runtime Settings](#runtime-settings)
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

1. **Generate** — Admin sends `/generate` in Telegram (or creates a post in the web dashboard), picks a post type and topic, chooses a format (text, image, branded card, or video)
2. **Review** — The bot shows a preview with action buttons, or the dashboard shows a slide-over editor with approve/reject/regenerate actions
3. **Publish** — On approval, the post is published to Telegram channel + Instagram/YouTube (if configured). Scheduled posts are auto-published by a background worker

```
Admin Chat / Web Dashboard       Monolith Backend                Platforms
──────────────────────────       ────────────────                ─────────
/generate or Dashboard UI        FastAPI + background tasks      Telegram Channel
  → post type                      → text via OpenRouter         Instagram
  → topic                         → images via OpenRouter        YouTube Shorts
  → format                        → branded cards via Pillow
      ↓                           → videos via OpenAI
  Review preview                   → scheduled publishing
  [Approve] [Schedule]             → token refresh
  [Edit] [Regenerate]
  [Reject]
      ↓
  Published
```

---

## Architecture

The backend runs as a **single monolith process**. FastAPI serves the REST API and launches all background services (Telegram bot, generation worker, publish worker, video worker, token refresher) as asyncio tasks. Services are **gracefully skipped** when their required tokens are missing — you can start the app with zero tokens and configure everything through the Settings page.

```
┌──────────────────────────────────────────────────────────────┐
│                  MONOLITH BACKEND (FastAPI)                   │
│                                                              │
│  REST API  ←→  React SPA (JWT auth)                          │
│  Telegram Bot (aiogram 3)                                    │
│  Generation Worker    ──→ text / image / video generation    │
│  Publish Worker       ──→ scheduled post publishing          │
│  Video Worker         ──→ long-running video pipeline        │
│  Token Refresher      ──→ Instagram OAuth refresh            │
│                                                              │
│  Services auto-skip when tokens are not configured           │
└────────────────────────┬─────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────────┐
│   Content   │ │  Publishing  │ │    Platforms      │
│   Engine    │ │   Engine     │ │                   │
│             │ │              │ │ Telegram Channel   │
│ Text Gen    │ │ Telegram     │ │ Instagram          │
│ Image Gen   │ │ Instagram    │ │ YouTube Shorts     │
│ Image Comp  │ │ YouTube      │ │                   │
│ Video Pipe  │ │ Manual       │ │                   │
└──────┬──────┘ └──────┬───────┘ └───────────────────┘
       │               │
       └───────────────┘
              ▼
┌───────────────────────────────┐
│          DATA LAYER           │
│  PostgreSQL    │    Redis     │
│  (posts, pubs, │  (task queue,│
│   themes,      │  video queue)│
│   settings)    │             │
└───────────────────────────────┘
```

### Docker Services (4 containers)

| Service | Purpose |
|---------|---------|
| `postgres` | PostgreSQL 17 database |
| `redis` | Redis 7 task queue |
| `backend` | Monolith: FastAPI API + Telegram bot + all workers |
| `frontend` | React SPA served by nginx (proxies `/api` to backend) |

### Background Tasks

| Task | Condition | Purpose |
|------|-----------|---------|
| `telegram_bot` | `TG_BOT_TOKEN` set | Telegram admin bot for content management |
| `generation_worker` | Always runs | Text/image/video generation queue processor |
| `publish_worker` | `TG_BOT_TOKEN` set | Auto-publishes scheduled posts every 30s |
| `video_worker` | `OPENAI_API_KEY` set | Long-running video generation (5–60 min per video) |
| `token_refresher` | Always runs | Refreshes Instagram OAuth tokens before expiry |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ and npm (for local frontend dev)
- Python 3.12+ (for local backend dev)

**No API tokens are required to start.** You can configure all tokens at runtime through the Settings page in the web dashboard.

### 1. Clone and Configure

```bash
git clone <repo-url> && cd marketing-is-easy
cp .env.example .env
```

Edit `.env` — at minimum, set the infrastructure and dashboard credentials:

```env
DATABASE_URL=postgresql+asyncpg://social:social_dev_pass@postgres:5432/social_marketing
REDIS_URL=redis://redis:6379/0
API_SECRET_KEY=your-random-secret-key
API_DEFAULT_ADMIN_PASSWORD=your-admin-password
```

All other tokens (Telegram, OpenRouter, OpenAI, Instagram, YouTube) can be configured later through the Settings page.

### 2. Start with Docker

```bash
make docker
# or: docker compose up --build
```

This starts **4 containers**: PostgreSQL, Redis, backend (monolith), and frontend.

- **Web Dashboard:** `http://localhost:3000`
- **API:** `http://localhost:8000`

The database tables and admin user are created automatically on first startup.

### 3. Configure Tokens

Open the web dashboard → **Settings** page → enter your API tokens → Save. Services start automatically when their required tokens are configured.

---

## Running in Docker

```bash
# Start all 4 services
make docker

# Stop everything
make docker-stop

# View logs
make logs              # all services
make logs SVC=backend  # backend only

# Rebuild and restart
docker compose up -d --build
```

---

## Running Locally (Dev)

### Prerequisites

```bash
pip install -e ".[dev]"
cd frontend && npm install && cd ..
```

### Using Make

```bash
# Show all available commands
make help

# Start infra (PostgreSQL + Redis) + monolith backend + frontend dev server
make dev

# Or run individual components:
make infra           # Start PostgreSQL + Redis in Docker
make migrate         # Run database migrations
make admin           # Create admin user (uses env vars)
make api             # Start monolith backend with hot reload (port 8000)
make frontend-dev    # Start frontend dev server (port 5173)
```

For local development, use `localhost` variants of `DATABASE_URL` and `REDIS_URL` in `.env`:

```env
DATABASE_URL=postgresql+asyncpg://social:social_dev_pass@localhost:5432/social_marketing
REDIS_URL=redis://localhost:6379/0
```

### Manual Setup

#### 1. Start Infrastructure

```bash
docker compose up -d postgres redis
```

#### 2. Run Database Migrations

```bash
alembic upgrade head
```

#### 3. Start Backend + Frontend

```bash
# Terminal 1: Monolith backend (API + bot + all workers)
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend dev server (proxies /api to :8000)
cd frontend && npm run dev
```

#### 4. Test It

- **Web Dashboard:** Open `http://localhost:5173`, log in with your admin credentials
- **Telegram Bot:** Configure `TG_BOT_TOKEN` in Settings, then send `/generate` in your admin chat

---

## Running on a VM

To deploy on a remote VM with SSH tunnels for development:

```bash
# Deploy (pull latest + rebuild Docker)
make deploy

# Open SSH tunnels to expose local services on VM
make tunnel            # Both frontend (3005) and API (8000)
make tunnel-frontend   # Frontend only (port 3005)
make tunnel-api        # API only (port 8000)
```

---

## Web Dashboard

The web dashboard provides a full-featured UI for managing content, built with React 19, TypeScript, and Tailwind CSS.

### Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Stats overview, upcoming posts timeline, attention cards |
| Calendar | `/calendar` | Week view of scheduled posts with status filtering |
| Themes | `/themes` | Content themes with batch generation |
| Theme Detail | `/themes/:id` | Theme posts, stats, and settings |
| Channels | `/channels/:platform` | Platform account settings and post history |
| Content Library | `/library` | Media asset management |
| Settings | `/settings` | API tokens, service status, runtime configuration |

### Post Editor

Click any post to open the slide-over editor panel with tabs:

- **Content** — Text, image, and video sections with generate/regenerate buttons
- **Platforms** — Per-platform text variants with character count validation
- **Schedule** — Date/time picker for scheduling publication
- **History** — Post activity log

### API Endpoints

All endpoints require JWT authentication (`POST /api/auth/login` to obtain a token).

| Group | Endpoints |
|-------|-----------|
| Auth | `POST /api/auth/login`, `GET /api/auth/me` |
| Posts | `GET/POST /api/posts`, `GET/PATCH/DELETE /api/posts/:id`, actions: `approve`, `reject`, `publish-now`, `generate-text/image/video` |
| Themes | `GET/POST /api/themes`, `GET/PATCH/DELETE /api/themes/:id`, `POST /api/themes/:id/batch-generate` |
| Calendar | `GET /api/calendar?start=&end=`, `PATCH /api/calendar/reschedule` |
| Dashboard | `GET /api/dashboard/stats\|upcoming\|attention` |
| Channels | `GET/PATCH /api/channels` |
| Assets | `GET/POST/DELETE /api/assets` |
| Settings | `GET/PUT /api/settings`, `DELETE /api/settings/{key}` |
| Health | `GET /api/health` |

---

## Runtime Settings

The Settings page allows you to configure API tokens and service settings without restarting. Settings are stored in the database and override environment variables.

### How It Works

1. On startup, the backend loads all settings from the `app_settings` database table
2. DB values override environment variables — env vars serve as defaults
3. When you update a setting through the UI, it takes effect immediately in memory
4. Secret values (API keys, tokens) are masked in the UI, showing only the last 4 characters

### Configurable Settings

| Group | Settings |
|-------|----------|
| Telegram | Bot Token, Admin Chat ID, Admin Thread ID, Channel ID, Admin User IDs |
| AI & Generation | OpenRouter API Key, Text Model, Image Model, OpenAI API Key |
| Instagram | Access Token, Business Account ID |
| YouTube | Client ID, Client Secret, Refresh Token |
| Brand & Content | Brand Name, Content Tone, Default Hashtags, Track, Language |

### Service Status

The Settings page also shows the status of all background services (running/stopped). Services automatically start when their required tokens become available on the next restart.

---

## Configuration

All configuration is via environment variables (see `.env.example`). API tokens can also be configured at runtime through the Settings page.

### Infrastructure (required)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `REDIS_URL` | — | Redis connection string |
| `API_SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `API_CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |
| `API_DEFAULT_ADMIN_USERNAME` | `admin` | Auto-created admin username |
| `API_DEFAULT_ADMIN_PASSWORD` | (empty) | Set to auto-create admin user on startup |

### Telegram

| Variable | Description |
|----------|-------------|
| `TG_BOT_TOKEN` | Telegram bot token from @BotFather |
| `TG_ADMIN_CHAT_ID` | Chat ID where you review posts |
| `TG_ADMIN_THREAD_ID` | Thread ID in the admin chat (optional) |
| `TG_CHANNEL_ID` | Target Telegram channel ID |
| `TG_ADMIN_USER_IDS` | Comma-separated Telegram user IDs with admin access |

### AI & Generation

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key for text/image generation |
| `OPENROUTER_TEXT_MODEL` | Text generation model (default: `mistralai/mistral-small-creative`) |
| `OPENROUTER_IMAGE_MODEL` | Image generation model (default: `black-forest-labs/flux.2-flex`) |
| `OPENAI_API_KEY` | OpenAI API key (for video pipeline) |

### Instagram

| Variable | Description |
|----------|-------------|
| `MEDIA_BASE_URL` | Public URL where media files are served (**required for Instagram**) |
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived Instagram access token (60-day, auto-refreshed) |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram Business account ID |

### YouTube

| Variable | Description |
|----------|-------------|
| `YOUTUBE_CLIENT_ID` | Google Cloud OAuth 2.0 client ID |
| `YOUTUBE_CLIENT_SECRET` | Google Cloud OAuth 2.0 client secret |
| `YOUTUBE_REFRESH_TOKEN` | Obtained via `scripts/setup_oauth.py` |

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

Scheduled posts sit at `approved` until their `scheduled_at` time, then the publish worker picks them up.

---

## Publishing

### Telegram

Always available. Publishes text, photos, and videos to the configured channel. No special setup beyond the bot token and channel ID.

### Instagram

Publishes photos via the Meta Graph API v22. Requires a Facebook Business account linked to an Instagram Business/Creator account.

**Setup:**
1. Create a Facebook App with Instagram Graph API permissions
2. Generate a long-lived access token (60 days)
3. Set `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_BUSINESS_ACCOUNT_ID` (via Settings page or `.env`)
4. Serve media files at a public URL (`MEDIA_BASE_URL`)

The token refresher auto-refreshes tokens 10 days before expiry.

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

The video pipeline transforms text content into polished 30–60 second vertical shorts. It runs as a background task in the monolith because generation can take 5–60 minutes.

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
│   │   ├── settings.py                  # DynamicSettings wrapper (DB overrides → env vars)
│   │   └── settings_registry.py         # Configurable settings metadata (groups, labels)
│   ├── db/
│   │   ├── models.py                    # SQLAlchemy models (Post, Theme, AppSetting, etc.)
│   │   ├── repo.py                      # Repository classes (PostRepo, PublicationRepo)
│   │   ├── theme_repo.py               # ThemeRepo with stats aggregation
│   │   └── settings_repo.py            # AppSetting CRUD (get/set/delete with upsert)
│   ├── api/
│   │   ├── main.py                      # Monolith entry point (API + background tasks)
│   │   ├── auth.py                      # JWT auth, password hashing, get_current_user
│   │   ├── deps.py                      # Dependency injection (get_db)
│   │   ├── schemas/                     # Pydantic request/response models
│   │   │   ├── auth.py, post.py, theme.py, calendar.py
│   │   │   ├── dashboard.py, channel.py, asset.py
│   │   │   ├── settings.py             # Settings API schemas
│   │   │   └── common.py               # PaginatedResponse, ErrorResponse
│   │   └── routers/                     # API route handlers
│   │       ├── auth.py                  # Login, get current user
│   │       ├── posts.py                 # CRUD + generate + approve/reject/publish
│   │       ├── themes.py               # CRUD + batch generate
│   │       ├── calendar.py             # Date-range queries, reschedule
│   │       ├── dashboard.py            # Stats, upcoming, attention
│   │       ├── channels.py             # Platform account management
│   │       ├── assets.py               # Media file management
│   │       └── settings.py            # Runtime settings CRUD (GET/PUT/DELETE)
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
│   │   ├── bot.py                       # Bot entry point with run() for monolith
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
├── frontend/
│   ├── src/
│   │   ├── main.tsx                     # Entry point
│   │   ├── App.tsx                      # Providers, routing, auth guard
│   │   ├── api/                         # Typed API client (get/post/patch/put/del)
│   │   │   └── settings.ts            # Settings + health API functions
│   │   ├── hooks/                       # TanStack Query hooks + query keys
│   │   │   └── useSettings.ts         # Settings + health hooks
│   │   ├── stores/                      # Zustand stores (ui, editor)
│   │   ├── pages/                       # Route pages (Dashboard, Calendar, Settings, etc.)
│   │   ├── components/
│   │   │   ├── layout/                  # Sidebar, SlideOverPanel, Layout
│   │   │   ├── dashboard/              # StatsRow, UpcomingTimeline, AttentionCards
│   │   │   ├── calendar/               # WeekView, DayColumn, CalendarPostCard
│   │   │   ├── post-editor/            # PostEditorPanel, ContentTab, tabs
│   │   │   ├── themes/                 # ThemeCard, ThemeHeader, PostRow
│   │   │   └── shared/                 # StatusBadge, PlatformIcon, EmptyState
│   │   ├── lib/                         # Types, constants, date utils, platform config
│   │   └── styles/globals.css           # Tailwind + CSS custom properties
│   ├── package.json
│   ├── vite.config.ts                   # Dev proxy /api → :8000
│   ├── Dockerfile                       # Multi-stage: node build → nginx serve
│   └── nginx.conf                       # Proxies /api + /media to backend
├── migrations/
│   └── versions/
│       ├── 001_initial_schema.py       # Base database schema
│       ├── 002_add_themes_and_api_support.py  # Themes, API users, post.theme_id
│       └── 003_add_app_settings.py    # Runtime settings table
├── templates/
│   └── fonts/                          # Roboto fonts (downloaded via script)
├── scripts/
│   ├── download_fonts.py              # Download Roboto fonts from Google
│   └── create_admin.py               # Create/update API admin user
├── docker-compose.yml                  # 4 services (postgres, redis, backend, frontend)
├── Dockerfile                          # Python 3.12 + ffmpeg (monolith backend)
├── Makefile                            # Dev commands (make dev, make docker, etc.)
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

8 tables managed via Alembic migrations:

- **posts** — Core content entity with status tracking, media URLs, generation params
- **post_publications** — Per-platform publish records (telegram, instagram_post, youtube_short)
- **content_sources** — Input data for content generation (articles, supplements, manual)
- **platform_accounts** — OAuth credentials and token expiry tracking
- **content_templates** — Reusable content/image templates
- **themes** — Content themes with cadence rules, target platforms, and generation context
- **api_users** — Web dashboard user accounts with hashed passwords
- **app_settings** — Runtime key-value settings (DB overrides for env vars, with secret masking)

Tables are auto-created on first startup. For production, use:

```bash
alembic upgrade head
```

---

## Troubleshooting

**Bot doesn't respond to commands:**
- Verify `TG_BOT_TOKEN` is correct (check Settings page → Telegram group)
- Verify your Telegram user ID is in `TG_ADMIN_USER_IDS`
- Check backend logs: `docker compose logs backend`

**Web dashboard login fails:**
- Ensure `API_DEFAULT_ADMIN_PASSWORD` is set in `.env`
- The admin user is auto-created on API startup
- Or create manually: `make admin` or `python -m scripts.create_admin admin your-password`

**Frontend can't reach API (local dev):**
- Vite dev server proxies `/api` to `http://localhost:8000` — ensure the backend is running
- Check that `DATABASE_URL` and `REDIS_URL` use `localhost` (not `postgres`/`redis`)

**Services show as "stopped" in Settings:**
- Services only start when their required tokens are configured
- After adding tokens via Settings, restart the backend for the services to start
- Check `GET /api/health` for service status

**Images not publishing to Instagram:**
- Instagram requires `MEDIA_BASE_URL` pointing to publicly accessible media files
- Check that `INSTAGRAM_ACCESS_TOKEN` is valid (tokens expire after 60 days)
- The token refresher auto-renews tokens 10 days before expiry

**Video generation takes too long:**
- sora-2 motion clips can take 5–60 minutes per scene
- Set `VIDEO_ENABLE_MOTION=false` for instant still-image videos
- Check backend logs: `docker compose logs backend`

**Scheduled posts not publishing:**
- Ensure publish worker is running (check `GET /api/health`)
- It checks every 30 seconds for posts where `status=approved` and `scheduled_at <= now`
- Requires `TG_BOT_TOKEN` to be configured
