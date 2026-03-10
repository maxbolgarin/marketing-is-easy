# Social Marketing Frontend — Architecture Document

**Version:** 1.0  
**Date:** March 2026  
**Status:** Design Phase  

---

## 1. Core Concept Rethink

Before jumping into screens, there are a few fundamental design tensions in the original idea that need resolving.

### 1.1 The Platform-Centric vs Content-Centric Dilemma

The original idea has platform pages (Telegram, Instagram, YouTube, Twitter, Email) in the main navigation. This implies a platform-first workflow: "I'm working on Instagram today."

But in practice, social marketing is content-first: "I have something to say, and it goes to multiple platforms with adaptations." A supplement spotlight post might become a Telegram text post, an Instagram carousel, AND a YouTube Short — all from the same content brief.

**Resolution: Hybrid navigation.** The primary workspace is content-centric (Dashboard, Calendar, Themes). Platform pages exist but serve as filtered views + platform-specific settings, not as separate content silos.

### 1.2 What is a "Theme" Really?

The original idea describes themes as groupings where posts share a topic. This is useful but needs clearer definition. A theme is essentially a content campaign — a container that provides:

- Shared topic/angle (e.g., "Sleep Optimization Series", "Myth Busting Mondays")
- Visual consistency (color palette, template style)
- Scheduling cadence (e.g., every Monday, or specific date range)
- Platform targets (which platforms this theme publishes to)
- Generation context (LLM gets theme context for consistency across posts)

A theme is NOT just a folder. It carries semantic meaning that influences both generation and scheduling.

### 1.3 The Post is a Bundle, Not a Single Object

A single "post" in the user's mind is actually a content brief that produces multiple platform-specific publications. The data model must reflect this:

```
ContentBrief (what the user creates/edits)
  ├── text prompt or static text
  ├── image prompt or static image
  ├── video prompt or static video
  └── PlatformVariant[] (auto-generated or manually adjusted)
       ├── telegram: long text + image
       ├── instagram_post: short caption + square image
       ├── instagram_reel: 30s video + caption
       ├── youtube_short: 60s video + description
       └── twitter: 280 chars + image
```

The UI should let you work at the brief level (one editor) while previewing/tweaking per-platform variants.

---

## 2. Information Architecture

### 2.1 Navigation Structure

```
┌─────────────────────────────────────────────────┐
│  SIDEBAR (left, collapsible)                     │
│                                                  │
│  ● Dashboard          — Overview + quick actions │
│  ● Calendar           — Visual schedule          │
│  ● Themes             — Campaign management      │
│  ● Content Library     — Assets & templates      │
│  ─────────────────                               │
│  CHANNELS                                        │
│  ○ Telegram           — TG-specific view         │
│  ○ Instagram          — IG-specific view         │
│  ○ YouTube            — YT-specific view         │
│  ○ Twitter/X          — X-specific view          │
│  ○ Email              — Email-specific view      │
│  ─────────────────                               │
│  ○ Settings           — Accounts, API keys       │
└─────────────────────────────────────────────────┘
```

Why this order:
- Dashboard/Calendar/Themes are the daily-use views (content-first)
- Channel pages are secondary views for platform-specific tuning
- Settings is bottom-anchored (rarely used)

### 2.2 Page Hierarchy

```
Dashboard
├── Stats row (posts this week, pending review, published, engagement)
├── Upcoming posts (next 48h, compact timeline)
├── Action cards (quick generate, pending reviews, failed posts)
└── Recent activity feed

Calendar
├── View toggle: Week / Month / List
├── Day columns with post cards (drag-and-drop)
├── Filter bar: by theme, platform, status
└── Quick-add: click empty slot → create post

Themes
├── Theme list (cards with stats: post count, next publish, platforms)
├── Theme detail page
│   ├── Theme header (name, description, platforms, cadence, status)
│   ├── Mini calendar (this theme's posts only)
│   └── Post list (within this theme)
│       └── Post editor (inline or modal)

Channel Pages (Telegram, Instagram, YouTube, Twitter, Email)
├── Calendar strip (week view, this channel only)
├── Post list (filtered to this channel)
├── Channel-specific settings (account, templates, defaults)
└── Analytics (if connected)

Content Library
├── Image assets (uploaded + AI-generated)
├── Video assets
├── Text templates / prompt presets
└── Brand assets (logos, fonts, color palettes)

Settings
├── Connected accounts (OAuth status, token health)
├── API keys (OpenRouter, fal.ai)
├── Team / access (future)
├── Brand profile (name, tone, default hashtags per channel)
└── Generation defaults (models, temperature, etc.)
```

---

## 3. Core Entity Model (Frontend Perspective)

### 3.1 Entity Relationships

```
Theme (1) ──── has many ────── (N) Post
Post  (1) ──── has many ────── (N) PlatformVariant
Post  (1) ──── has many ────── (N) MediaAsset
Theme (1) ──── targets many ── (N) Channel

Channel: { platform, account_id, display_name, status, config }
```

### 3.2 Theme

```
Theme {
  id: UUID
  name: string                           // "Sleep Optimization Series"
  description: string                    // Brief for LLM context
  status: "active" | "paused" | "completed" | "draft"
  
  // Targeting
  target_platforms: Platform[]           // ["telegram", "instagram_post", "youtube_short"]
  
  // Scheduling
  cadence_type: "manual" | "recurring"
  cadence_rule: CadenceRule | null       // { frequency: "weekly", days: ["mon", "thu"], time: "09:00" }
  start_date: Date | null
  end_date: Date | null
  
  // Generation context
  generation_context: string             // Persistent LLM context for all posts in theme
  default_prompt_template: string | null // Prompt skeleton for new posts
  
  // Visual
  color: string                          // UI accent color for calendar
  template_id: UUID | null               // Default image template
  
  // Stats (computed)
  post_count: number
  published_count: number
  next_publish_at: DateTime | null
}
```

### 3.3 Post (Content Brief)

```
Post {
  id: UUID
  theme_id: UUID | null                  // Can exist without theme
  
  // Identity
  title: string                          // Internal reference name
  post_type: "single" | "recurring"
  recurrence_rule: RecurrenceRule | null  // For recurring: { every: "week", count: 8 }
  
  // Content — the "brief"
  content: {
    mode: "static" | "generated" | "hybrid"
    
    // Text
    text_static: string | null           // Hand-written text
    text_prompt: string | null           // LLM prompt for generation
    text_generated: string | null        // LLM output (editable after generation)
    text_model: string | null
    text_status: "empty" | "generating" | "generated" | "edited" | "final"
    
    // Image
    image_mode: "none" | "upload" | "generate" | "template"
    image_prompt: string | null
    image_template_id: UUID | null
    image_assets: MediaAsset[]
    image_status: "empty" | "generating" | "generated" | "uploaded" | "final"
    
    // Video
    video_mode: "none" | "upload" | "generate"
    video_prompt: string | null
    video_script: string | null          // Generated or hand-written script
    video_assets: MediaAsset[]
    video_status: "empty" | "generating" | "generated" | "uploaded" | "final"
  }
  
  // Scheduling
  scheduled_at: DateTime | null
  timezone: string
  
  // Status
  status: "draft" | "generating" | "review" | "approved" | "scheduled" | 
          "publishing" | "published" | "failed" | "rejected"
  
  // Platform variants (auto-populated based on theme targets or manually added)
  variants: PlatformVariant[]
  
  created_at: DateTime
  updated_at: DateTime
}
```

### 3.4 PlatformVariant

```
PlatformVariant {
  id: UUID
  post_id: UUID
  platform: "telegram" | "instagram_post" | "instagram_reel" | 
            "instagram_story" | "youtube_short" | "twitter" | "email"
  
  // Platform-adapted content (defaults from Post, overridable)
  text: string | null                    // Adapted text (length, hashtags, formatting)
  media_url: string | null               // Platform-specific media version
  
  // Platform-specific fields
  platform_config: {
    hashtags: string[] | null
    mentions: string[] | null
    link_url: string | null
    // Instagram: alt_text, location
    // YouTube: title, tags, category
    // Twitter: thread (boolean), poll options
    // Email: subject, preview_text, recipient_list
  }
  
  // Publishing
  status: "pending" | "ready" | "publishing" | "published" | "failed" | "skipped"
  published_at: DateTime | null
  platform_post_id: string | null
  platform_url: string | null
  error: string | null
}
```

### 3.5 MediaAsset

```
MediaAsset {
  id: UUID
  type: "image" | "video" | "audio"
  source: "upload" | "generated" | "template"
  url: string
  thumbnail_url: string | null
  metadata: {
    width: number
    height: number
    duration_sec: number | null          // For video/audio
    file_size: number
    mime_type: string
    generation_prompt: string | null
    generation_model: string | null
  }
  created_at: DateTime
}
```

---

## 4. Page Layouts (Wireframe Descriptions)

### 4.1 Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: "Dashboard"                              [+ New Post ▾] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ 12       │ │ 3        │ │ 47       │ │ 2        │           │
│  │ This Week│ │ Pending  │ │ Published│ │ Failed   │           │
│  │ Scheduled│ │ Review   │ │ This Mo. │ │          │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                  │
│  UPCOMING (next 48h)                                            │
│  ┌──────────────────────────────────────────────────────┐       │
│  │ Timeline: [Today 14:00] [Today 18:00] [Tomorrow 9:00]│       │
│  │           TG post       IG reel       TG+IG post    │       │
│  │           "Sleep tip"   "Myth #4"     "Magnesium"   │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  NEEDS ATTENTION                                                 │
│  ┌────────────────────┐ ┌────────────────────┐                  │
│  │ 👀 3 Posts Pending │ │ ❌ 2 Failed Posts  │                  │
│  │    Review          │ │    Retry / Check   │                  │
│  │    [Review All →]  │ │    [View →]        │                  │
│  └────────────────────┘ └────────────────────┘                  │
│                                                                  │
│  ACTIVE THEMES                                                   │
│  ┌─────────────────────────────────────────────┐                │
│  │ 🟢 Sleep Series      8/12 posts │ TG IG    │                │
│  │ 🟢 Myth Busting Mon  4/∞ posts  │ TG IG YT │                │
│  │ 🟡 Nootropics Guide  0/6 posts  │ TG       │  (paused)     │
│  └─────────────────────────────────────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Calendar

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: "Calendar"   [◀ Week ▶]  [Week|Month|List] [Filter ▾]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Mon 10     Tue 11     Wed 12     Thu 13     Fri 14     ...     │
│  ─────────  ─────────  ─────────  ─────────  ─────────          │
│  ┌───────┐                        ┌───────┐                     │
│  │09:00  │             ┌───────┐  │09:00  │                     │
│  │🟦 TG  │             │14:00  │  │🟧 IG  │                     │
│  │Sleep#5│             │🟦 TG  │  │Myth#4 │                     │
│  │✅ appr│             │Magnesi│  │👀 revw│                     │
│  └───────┘             │📝 drft│  └───────┘                     │
│                        └───────┘  ┌───────┐                     │
│  ┌───────┐                        │18:00  │                     │
│  │18:00  │                        │🟥 YT  │                     │
│  │🟧 IG  │                        │Reel#2 │                     │
│  │Sleep#5│                        │⏳ gen │                     │
│  │✅ appr│                        └───────┘                     │
│  └───────┘                                                       │
│                                                                  │
│  ─── Legend ──────────────────────────────────────               │
│  🟦 Telegram  🟧 Instagram  🟥 YouTube  🟪 Twitter              │
│  Theme colors shown as left border on post cards                │
│                                                                  │
│  [+ Click any empty slot to create a post]                      │
│  [Drag post cards to reschedule]                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Key interactions:
- Click empty slot → create new post at that day/time
- Drag post card → reschedule to new slot
- Click post card → open post detail (slide-over panel or modal)
- Filter by: theme (color-coded), platform, status
- Month view: shows dots/counts per day, click to zoom into day

### 4.3 Theme Detail Page

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: "← Themes / Sleep Optimization Series"  [⚙ Settings]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Theme: Sleep Optimization Series              [🟢 Active]│   │
│  │ "Evidence-based tips for better sleep quality"           │   │
│  │ Platforms: TG IG  │  Cadence: Mon & Thu 09:00           │   │
│  │ Progress: 8 of 12 published  │  Next: Thu Mar 13 09:00  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  CALENDAR STRIP (theme posts only)                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ [◀] Mon10  Tue11  Wed12  Thu13  Fri14  Sat15  Sun16 [▶] │   │
│  │      #5                   #6                              │   │
│  │     ✅✅                  📝                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  POSTS                                    [+ Add Post] [⚡Batch]│
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ #8  "Melatonin timing"     📝 Draft    Thu Mar 20       │   │
│  │     Text: ⏳ not generated  Image: ⏳ none               │   │
│  │     Platforms: [TG ✓] [IG ✓]                             │   │
│  │     [Generate ▶] [Edit] [Schedule]                        │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ #7  "Blue light filters"   👀 Review   Mon Mar 17       │   │
│  │     Text: ✅ generated      Image: ✅ generated           │   │
│  │     Platforms: [TG ✅] [IG 👀]                            │   │
│  │     [Approve] [Edit] [Regenerate] [Preview ▶]            │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ #6  "Magnesium glycinate"  ✅ Scheduled Thu Mar 13 09:00 │   │
│  │     Text: ✅ final          Image: ✅ final               │   │
│  │     Platforms: [TG ✅] [IG ✅]                             │   │
│  │     [Preview ▶] [Reschedule] [Unschedule]                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 Post Editor (Slide-Over Panel)

This is the most complex UI — a panel that slides in from the right when you click a post. It has tabs for content, platform variants, and scheduling.

```
┌───────────────────────────────────────────────┐
│ POST EDITOR                            [✕]    │
│ Theme: Sleep Series / Post #7                 │
│ Status: 👀 Review                             │
├───────────────────────────────────────────────┤
│ [Content] [Platforms] [Schedule] [History]     │
├───────────────────────────────────────────────┤
│                                               │
│ CONTENT TAB                                   │
│                                               │
│ Title (internal):                             │
│ ┌───────────────────────────────────────────┐ │
│ │ Blue light and sleep quality              │ │
│ └───────────────────────────────────────────┘ │
│                                               │
│ ── TEXT ───────────────────────────────────── │
│ Mode: [Static ○] [Generated ●] [Hybrid ○]    │
│                                               │
│ Prompt:                                       │
│ ┌───────────────────────────────────────────┐ │
│ │ Write about how blue light from screens   │ │
│ │ affects melatonin production and sleep     │ │
│ │ quality. Include practical tips for        │ │
│ │ reducing exposure in the evening.          │ │
│ └───────────────────────────────────────────┘ │
│ [🔄 Generate]  Model: [Claude Sonnet 4 ▾]    │
│                                               │
│ Generated text:              [✏️ Edit] [🔄]   │
│ ┌───────────────────────────────────────────┐ │
│ │ Did you know that just 2 hours of screen  │ │
│ │ time before bed can suppress melatonin    │ │
│ │ production by up to 22%?                  │ │
│ │                                           │ │
│ │ Research shows that blue light (450-490nm)│ │
│ │ is particularly effective at activating...│ │
│ │ ...                                       │ │
│ └───────────────────────────────────────────┘ │
│ Status: ✅ Generated (342 words)              │
│                                               │
│ ── IMAGE ──────────────────────────────────── │
│ Mode: [None ○] [Upload ○] [Generate ●]       │
│       [Template ○]                            │
│                                               │
│ Prompt:                                       │
│ ┌───────────────────────────────────────────┐ │
│ │ Serene bedroom at night with warm ambient │ │
│ │ lighting, no screens visible, calming     │ │
│ │ atmosphere, photorealistic                │ │
│ └───────────────────────────────────────────┘ │
│ [🔄 Generate]  Aspect: [1:1 ▾]               │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │                                           │ │
│ │          [Generated image preview]        │ │
│ │              1080 × 1080                  │ │
│ │                                           │ │
│ └───────────────────────────────────────────┘ │
│ [↻ Regenerate] [✂ Crop] [Replace ↑]          │
│                                               │
│ ── VIDEO ──────────────────────────────────── │
│ Mode: [None ●] [Upload ○] [Generate ○]       │
│                                               │
│                                               │
│ ────────────────────────────────────────────  │
│ [Mark as Final ✓] [Send to Review →]          │
│                                               │
└───────────────────────────────────────────────┘
```

### 4.5 Platform Variants Tab (within Post Editor)

```
┌───────────────────────────────────────────────┐
│ [Content] [Platforms] [Schedule] [History]     │
├───────────────────────────────────────────────┤
│                                               │
│ PLATFORM VARIANTS                             │
│ Auto-adapted from your content brief.         │
│ Edit per-platform if needed.                  │
│                                               │
│ ┌─── 📢 Telegram ─────────────────── [✓ On]─┐│
│ │                                            ││
│ │ Preview:                                   ││
│ │ ┌────────────────────────────────────────┐ ││
│ │ │ Did you know that just 2 hours of      │ ││
│ │ │ screen time before bed can suppress    │ ││
│ │ │ melatonin production by up to 22%?     │ ││
│ │ │ ...                                    │ ││
│ │ │                                        │ ││
│ │ │ #biohacking #sleep #health #biomaxing  │ ││
│ │ └────────────────────────────────────────┘ ││
│ │ Characters: 487 / 4096          [✏️ Edit]  ││
│ │ Status: ✅ Ready                           ││
│ └────────────────────────────────────────────┘│
│                                               │
│ ┌─── 📷 Instagram Post ─────────── [✓ On]───┐│
│ │                                            ││
│ │ Preview:                                   ││
│ │ ┌──────────┐ ┌───────────────────────────┐ ││
│ │ │  Image   │ │ Short caption version...  │ ││
│ │ │ preview  │ │ + hashtags (auto-adapted) │ ││
│ │ │ 1080²    │ │                           │ ││
│ │ └──────────┘ └───────────────────────────┘ ││
│ │ Characters: 312 / 2200          [✏️ Edit]  ││
│ │ Hashtags: [✏️ Edit tags]                   ││
│ │ Status: ✅ Ready                           ││
│ └────────────────────────────────────────────┘│
│                                               │
│ ┌─── 🎬 YouTube Short ──────────── [○ Off]──┐│
│ │ Enable to create a YouTube Short variant   ││
│ │ from this post's content.                  ││
│ └────────────────────────────────────────────┘│
│                                               │
└───────────────────────────────────────────────┘
```

### 4.6 Channel Page (e.g., Instagram)

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER: "Instagram"  Account: @biomaxing  [🟢 Connected]       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ CALENDAR STRIP (IG posts only)                                  │
│ ┌──────────────────────────────────────────────────────────┐    │
│ │ [◀] Mon10  Tue11  Wed12  Thu13  Fri14  Sat15  Sun16 [▶] │    │
│ │      📷           📷     📷🎬                             │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│ UPCOMING POSTS                                                   │
│ ┌──────────────────────────────────────────────────────────┐    │
│ │ ┌──────┐  "Sleep tip #5"     Post │ Mon 10 09:00        │    │
│ │ │ img  │  Caption preview... ✅ Approved                 │    │
│ │ └──────┘  [Preview] [Reschedule]                         │    │
│ ├──────────────────────────────────────────────────────────┤    │
│ │ ┌──────┐  "Myth: More protein"  Reel │ Thu 13 18:00     │    │
│ │ │ vid  │  Script preview...  👀 Review                   │    │
│ │ └──────┘  [Preview] [Approve] [Edit]                     │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│ CHANNEL SETTINGS                                                 │
│ ┌──────────────────────────────────────────────────────────┐    │
│ │ Default hashtags: #biohacking #supplements #biomaxing    │    │
│ │ Default posting times: 09:00, 18:00                      │    │
│ │ Image template: [BioMaxing Card v2 ▾]                    │    │
│ │ Account: @biomaxing (Business) │ Token expires: Apr 28   │    │
│ │ [Refresh Token] [Disconnect]                              │    │
│ └──────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Key User Flows

### 5.1 Create & Publish a Post (Happy Path)

```
1. User clicks [+ New Post] on Dashboard
   OR clicks empty calendar slot
   OR clicks [+ Add Post] in a Theme
   
2. Post Editor opens (slide-over panel)
   - If from Theme: theme is pre-selected, platforms pre-filled
   - If from Calendar: date/time pre-filled
   - If from Dashboard: blank

3. User fills in content brief:
   a. Selects text mode: Generated
   b. Writes prompt: "Write about magnesium glycinate for sleep"
   c. Clicks [Generate] → loading spinner → text appears
   d. Reviews text, optionally edits inline
   e. Selects image mode: Generate
   f. Writes image prompt → clicks [Generate] → image appears
   
4. Platform variants auto-populate:
   - Telegram: full text + hashtags
   - Instagram: shortened text + image + IG hashtags
   - User can toggle platforms on/off, edit per-platform text

5. User clicks [Send to Review]
   - Status: review
   - Admin bot also notified in Telegram (bidirectional)
   
6. User (or another admin) reviews:
   - Clicks [Approve] on each platform variant
   - OR [Approve All]
   - Selects schedule time (or "now")

7. Publish worker handles the rest
   - Status updates live via WebSocket/polling
   - Published posts show platform links
```

### 5.2 Batch Generate a Week's Content

```
1. User opens a Theme → clicks [⚡ Batch Generate]

2. Modal shows:
   - Theme context (pre-filled)
   - Number of posts to generate: [5]
   - Date range: [Mon Mar 10 – Fri Mar 14]
   - Cadence: [One per day at 09:00]
   - Content type: [Text + Image]
   
3. User clicks [Generate Batch]
   - Creates 5 post drafts with status "generating"
   - Each gets a prompt derived from theme context + variation
   - Progress shown: 1/5... 2/5... 3/5...
   
4. All posts appear in Theme's post list
   - User reviews each one
   - Approve individually or bulk-approve
```

### 5.3 Recurring Post Template

```
1. User creates a Theme "Myth Busting Monday"
   - Cadence: Every Monday at 09:00
   - Platforms: TG + IG

2. User creates a Post with type "recurring"
   - Prompt template: "Bust a common myth about {topic}"
   - The {topic} variable is filled each week
   
3. Each week (or via batch):
   - System creates a new Post instance from the template
   - Fills in topic from content source queue
   - Generates text + image
   - Sends for review
```

---

## 6. State Management Architecture

### 6.1 Recommended Approach

Given the app complexity (real-time updates, optimistic UI, cross-entity relationships), use:

**Zustand** for global state + **TanStack Query (React Query)** for server state.

Rationale:
- Zustand: lightweight, no boilerplate, good for UI state (sidebar open, active filters, editor state)
- TanStack Query: handles caching, background refetching, optimistic updates, pagination — exactly what a dashboard with live-updating post statuses needs
- Avoids Redux complexity while maintaining predictability

### 6.2 Store Structure

```
// Zustand stores (UI state only)
uiStore: {
  sidebarCollapsed: boolean
  activePanel: "editor" | "preview" | null
  activePanelPostId: UUID | null
  calendarView: "week" | "month" | "list"
  calendarDate: Date                     // Current week/month anchor
  filters: {
    themes: UUID[]
    platforms: Platform[]
    statuses: Status[]
  }
}

editorStore: {
  dirtyFields: Set<string>               // Track unsaved changes
  generationInProgress: {
    text: boolean
    image: boolean
    video: boolean
  }
  activeTab: "content" | "platforms" | "schedule" | "history"
}

// TanStack Query keys (server state)
queryKeys: {
  posts:        ["posts", { filters }]
  post:         ["posts", postId]
  themes:       ["themes", { filters }]
  theme:        ["themes", themeId]
  calendar:     ["calendar", { start, end, filters }]
  dashboard:    ["dashboard", "stats"]
  publications: ["posts", postId, "publications"]
  channels:     ["channels"]
  assets:       ["assets", { type, page }]
}
```

### 6.3 Real-Time Updates

Post statuses change asynchronously (generation completes, publish succeeds/fails). Two options:

**Option A: Polling (simpler, Phase 1)**
- TanStack Query's `refetchInterval` on active queries
- Calendar page: refetch every 30s
- Post editor (when generating): refetch every 3s
- Dashboard: refetch every 60s

**Option B: WebSocket (Phase 2+)**
- Server pushes status changes: `{ type: "post_status", post_id, new_status }`
- TanStack Query's cache is updated via `queryClient.setQueryData`
- Gives instant feedback when generation completes or post publishes

Start with Option A, migrate to B when the polling lag becomes annoying.

---

## 7. API Design (Backend-for-Frontend)

The existing backend is built for bot-driven workflows. The SPA needs a REST API layer. Recommended: **FastAPI** alongside the existing workers.

### 7.1 API Resource Structure

```
# Posts
GET    /api/posts                    # List posts (filterable by theme, platform, status, date range)
POST   /api/posts                    # Create post
GET    /api/posts/:id                # Get post with variants
PATCH  /api/posts/:id                # Update post (text, schedule, status)
DELETE /api/posts/:id                # Soft-delete post

# Post actions
POST   /api/posts/:id/generate-text  # Trigger text generation (async, returns immediately)
POST   /api/posts/:id/generate-image # Trigger image generation
POST   /api/posts/:id/generate-video # Trigger video generation
POST   /api/posts/:id/approve        # Approve for publishing
POST   /api/posts/:id/reject         # Reject post
POST   /api/posts/:id/publish-now    # Publish immediately

# Platform variants
GET    /api/posts/:id/variants       # Get all platform variants
PATCH  /api/posts/:id/variants/:vid  # Edit a specific variant
POST   /api/posts/:id/variants       # Add variant for new platform

# Themes
GET    /api/themes                   # List themes
POST   /api/themes                   # Create theme
GET    /api/themes/:id               # Get theme with stats
PATCH  /api/themes/:id               # Update theme
DELETE /api/themes/:id               # Archive theme
POST   /api/themes/:id/batch-generate # Generate batch of posts

# Calendar
GET    /api/calendar                 # Get posts in date range (optimized for calendar view)
PATCH  /api/calendar/reschedule      # Bulk reschedule (drag-and-drop)

# Channels
GET    /api/channels                 # List connected platform accounts
PATCH  /api/channels/:id             # Update channel settings
POST   /api/channels/:id/test        # Test connection

# Assets
GET    /api/assets                   # List media assets
POST   /api/assets/upload            # Upload file
DELETE /api/assets/:id               # Delete asset

# Dashboard
GET    /api/dashboard/stats          # Aggregated stats
GET    /api/dashboard/upcoming       # Next 48h posts
GET    /api/dashboard/attention      # Posts needing action

# Auth (simple for solo/small team)
POST   /api/auth/login               # Session-based or JWT
GET    /api/auth/me                  # Current user
```

### 7.2 Generation Response Pattern

Generation is async. The API triggers it and returns immediately. The frontend polls for completion.

```
POST /api/posts/:id/generate-text
Request:  { "prompt": "...", "model": "..." }
Response: { "status": "generating", "job_id": "..." }

GET /api/posts/:id
Response: {
  "content": {
    "text_status": "generating",    // ← frontend shows spinner
    "text_generated": null
  }
}

// ... after a few seconds ...

GET /api/posts/:id
Response: {
  "content": {
    "text_status": "generated",     // ← frontend shows result
    "text_generated": "Did you know that just 2 hours..."
  }
}
```

---

## 8. Component Architecture

### 8.1 Top-Level Layout

```
App
├── AuthProvider
├── QueryClientProvider
│   └── Layout
│       ├── Sidebar
│       │   ├── NavSection (Dashboard, Calendar, Themes, Library)
│       │   ├── ChannelSection (platform list with status dots)
│       │   └── SettingsLink
│       ├── MainContent (React Router outlet)
│       └── SlideOverPanel (Post Editor — renders on top of any page)
```

### 8.2 Key Component Tree

```
Pages:
  DashboardPage
  ├── StatsRow
  ├── UpcomingTimeline
  ├── AttentionCards
  └── ActiveThemes

  CalendarPage
  ├── CalendarToolbar (navigation, view toggle, filters)
  ├── WeekView / MonthView / ListView
  │   └── PostCard (draggable)
  └── FilterDrawer

  ThemesPage
  ├── ThemeList
  │   └── ThemeCard
  └── ThemeDetailPage
      ├── ThemeHeader
      ├── CalendarStrip
      └── PostList
          └── PostRow

  ChannelPage (parameterized by platform)
  ├── ChannelHeader (connection status)
  ├── CalendarStrip
  ├── ChannelPostList
  └── ChannelSettings

  ContentLibraryPage
  ├── AssetGrid
  ├── UploadDropzone
  └── AssetDetailModal

  SettingsPage
  ├── AccountsSection
  ├── APIKeysSection
  ├── BrandProfileSection
  └── GenerationDefaultsSection

Shared / Global:
  PostEditorPanel (slide-over, used from any page)
  ├── PostEditorHeader (title, status, close)
  ├── TabBar (Content, Platforms, Schedule, History)
  ├── ContentTab
  │   ├── TextSection
  │   │   ├── ModeToggle (static / generated / hybrid)
  │   │   ├── PromptInput (for generated mode)
  │   │   ├── GenerateButton (with model selector)
  │   │   └── TextEditor (editable output or static input)
  │   ├── ImageSection
  │   │   ├── ModeToggle (none / upload / generate / template)
  │   │   ├── PromptInput / UploadDropzone / TemplatePicker
  │   │   ├── GenerateButton
  │   │   └── ImagePreview (with crop/replace actions)
  │   └── VideoSection
  │       ├── ModeToggle (none / upload / generate)
  │       ├── ScriptEditor
  │       ├── GenerateButton
  │       └── VideoPreview
  ├── PlatformsTab
  │   └── PlatformVariantCard (per platform)
  │       ├── PlatformToggle (on/off)
  │       ├── TextPreview (adapted, editable)
  │       ├── MediaPreview (platform-specific crop)
  │       ├── CharacterCount
  │       └── HashtagEditor
  ├── ScheduleTab
  │   ├── DateTimePicker
  │   ├── TimezoneSelector
  │   └── RecurrenceConfig (if recurring)
  └── HistoryTab
      └── ActivityLog (status changes, generations, edits)
```

### 8.3 Component Design Principles

1. **Post Editor is a global singleton.** It renders as a slide-over panel on the right side, overlaying any page. This means you can open a post from Calendar, Theme, Channel page, or Dashboard without navigating away. URL updates to include `?post=uuid` for deep-linking.

2. **Calendar is drag-and-drop first.** Use a library like `@dnd-kit` for dragging post cards between day slots. Dropping triggers an optimistic update + PATCH to `/api/calendar/reschedule`.

3. **Generation states are inline, not modal.** When generating text/image/video, the section shows a loading skeleton in-place. No blocking modals. The user can switch tabs or close the panel — generation continues in background.

4. **Platform variants are auto-derived but overridable.** When text/image changes on the Content tab, platform variants auto-update (with character truncation, hashtag injection). But any manual edit on the Platforms tab "locks" that variant — it won't auto-update anymore. Show a "Reset to auto" link.

5. **Dual sync with Telegram bot.** Actions taken in the web UI should reflect in the admin bot, and vice versa. Both write to the same database; the web UI polls or receives WebSocket updates. Post approved in bot → web shows as approved on next refetch.

---

## 9. Technology Choices

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Framework** | React 19 + Vite | Fast builds, ecosystem maturity, wide hiring pool |
| **Routing** | React Router v7 | File-based or config routing, works with slide-over pattern |
| **State (UI)** | Zustand | Minimal boilerplate for UI state |
| **State (server)** | TanStack Query v5 | Caching, background refetch, optimistic updates |
| **Styling** | Tailwind CSS v4 | Utility-first, fast iteration, consistent with your Astro sites |
| **Components** | shadcn/ui | Copy-paste components, no dependency lock-in, Tailwind-native |
| **Calendar** | Custom (grid layout) or FullCalendar | FullCalendar has drag-and-drop built in; custom gives more control |
| **Drag & Drop** | @dnd-kit | Modern, accessible, works well with React 19 |
| **Forms** | React Hook Form + Zod | Type-safe validation, good with controlled/uncontrolled inputs |
| **Rich Text** | Tiptap (if needed) | For editing post text with minimal formatting |
| **Date Handling** | date-fns | Tree-shakeable, immutable |
| **HTTP** | ky or fetch wrapper | Lightweight, works with TanStack Query |
| **Icons** | Lucide React | Consistent with shadcn/ui |
| **Charts** | Recharts (if analytics needed) | Simple, React-native |

### Build & Deploy

| Concern | Choice |
|---------|--------|
| Build | Vite |
| TypeScript | Strict mode |
| Linting | Biome (replaces ESLint + Prettier, faster) |
| Testing | Vitest + Testing Library |
| Deployment | Static build → serve from same Docker Compose (nginx) or separate CDN |

---

## 10. File Structure

```
frontend/
├── index.html
├── vite.config.ts
├── tsconfig.json
├── biome.json
├── tailwind.config.ts
├── package.json
│
├── public/
│   └── favicon.svg
│
├── src/
│   ├── main.tsx                         # App entry
│   ├── App.tsx                          # Router + providers
│   │
│   ├── api/                             # API client layer
│   │   ├── client.ts                    # Base HTTP client (auth headers, base URL)
│   │   ├── posts.ts                     # Post CRUD + actions
│   │   ├── themes.ts                    # Theme CRUD
│   │   ├── calendar.ts                  # Calendar queries
│   │   ├── channels.ts                  # Channel queries
│   │   ├── assets.ts                    # Asset upload/list
│   │   ├── dashboard.ts                 # Dashboard stats
│   │   └── auth.ts                      # Auth endpoints
│   │
│   ├── hooks/                           # Custom hooks
│   │   ├── usePost.ts                   # TanStack Query hook for single post
│   │   ├── usePosts.ts                  # List with filters
│   │   ├── useTheme.ts
│   │   ├── useCalendar.ts
│   │   ├── useGeneration.ts             # Poll for generation status
│   │   ├── usePostEditor.ts             # Editor open/close + state
│   │   └── useDashboard.ts
│   │
│   ├── stores/                          # Zustand stores
│   │   ├── ui.ts                        # Sidebar, panel, filters
│   │   └── editor.ts                    # Editor-specific UI state
│   │
│   ├── pages/                           # Route pages
│   │   ├── Dashboard.tsx
│   │   ├── Calendar.tsx
│   │   ├── Themes.tsx
│   │   ├── ThemeDetail.tsx
│   │   ├── Channel.tsx                  # Parameterized: /channels/:platform
│   │   ├── ContentLibrary.tsx
│   │   ├── Settings.tsx
│   │   └── Login.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Layout.tsx               # Sidebar + main + panel
│   │   │   ├── Sidebar.tsx
│   │   │   └── SlideOverPanel.tsx       # Generic slide-over container
│   │   │
│   │   ├── post-editor/                 # The main editor panel
│   │   │   ├── PostEditorPanel.tsx       # Panel wrapper + tabs
│   │   │   ├── ContentTab.tsx
│   │   │   ├── TextSection.tsx
│   │   │   ├── ImageSection.tsx
│   │   │   ├── VideoSection.tsx
│   │   │   ├── PlatformsTab.tsx
│   │   │   ├── PlatformVariantCard.tsx
│   │   │   ├── ScheduleTab.tsx
│   │   │   ├── HistoryTab.tsx
│   │   │   └── GenerateButton.tsx       # Shared generate + model picker
│   │   │
│   │   ├── calendar/
│   │   │   ├── CalendarToolbar.tsx
│   │   │   ├── WeekView.tsx
│   │   │   ├── MonthView.tsx
│   │   │   ├── ListView.tsx
│   │   │   ├── DayColumn.tsx
│   │   │   ├── CalendarPostCard.tsx      # Draggable card
│   │   │   └── CalendarStrip.tsx         # Compact week strip (used in Theme/Channel pages)
│   │   │
│   │   ├── dashboard/
│   │   │   ├── StatsRow.tsx
│   │   │   ├── UpcomingTimeline.tsx
│   │   │   ├── AttentionCards.tsx
│   │   │   └── ActiveThemes.tsx
│   │   │
│   │   ├── themes/
│   │   │   ├── ThemeCard.tsx
│   │   │   ├── ThemeHeader.tsx
│   │   │   ├── PostRow.tsx
│   │   │   └── BatchGenerateModal.tsx
│   │   │
│   │   ├── channels/
│   │   │   ├── ChannelHeader.tsx
│   │   │   ├── ChannelPostList.tsx
│   │   │   └── ChannelSettings.tsx
│   │   │
│   │   └── shared/
│   │       ├── StatusBadge.tsx
│   │       ├── PlatformIcon.tsx
│   │       ├── MediaPreview.tsx
│   │       ├── UploadDropzone.tsx
│   │       ├── DateTimePicker.tsx
│   │       ├── ConfirmDialog.tsx
│   │       ├── EmptyState.tsx
│   │       └── LoadingSkeleton.tsx
│   │
│   ├── lib/                             # Utilities
│   │   ├── constants.ts                 # Platform colors, status labels, etc.
│   │   ├── date.ts                      # Date formatting helpers
│   │   ├── platform.ts                  # Platform-specific config/limits
│   │   └── types.ts                     # Shared TypeScript types
│   │
│   └── styles/
│       └── globals.css                  # Tailwind directives + custom properties
```

---

## 11. Key UX Decisions & Rationale

### 11.1 Slide-Over Editor vs Dedicated Page

**Decision:** Slide-over panel (right side, ~480px wide).

**Why:** The user needs to see context (calendar, theme list, channel queue) while editing a post. A full-page editor loses that context. The slide-over is the standard pattern for "detail editing within a list" (Linear, Notion, Asana all use this).

**Trade-off:** Less space for complex editors (especially video). Solution: the panel can expand to full-width for video editing, or video editing can be a dedicated modal within the panel.

### 11.2 Content Brief vs Direct Platform Editing

**Decision:** Content-first with auto-derived variants.

**Why:** Writing the same post 4 times for 4 platforms is the #1 pain point in social marketing. The user writes once, the system adapts. Manual per-platform editing is available but optional.

**The "lock" pattern:** When a user manually edits a platform variant, it becomes "locked" — no longer auto-updates from the brief. A small lock icon and "Reset to auto" link signal this clearly.

### 11.3 Generation as Inline Action vs Separate Step

**Decision:** Inline generation within the editor.

**Why:** Generation should feel like using a smart text field, not like submitting a job to a queue. Click "Generate" → spinner appears in-place → result fills the field. The user stays in flow.

**Technical:** This requires short polling (every 2–3s) while generating. TanStack Query's `refetchInterval` handles this cleanly: set to 3000ms when `text_status === "generating"`, disable when complete.

### 11.4 Calendar as Primary vs Secondary View

**Decision:** Calendar is a top-level page, not embedded in every channel page.

**Why:** The calendar is the "truth" of what happens when. Channel pages show a compact "calendar strip" (horizontal week view) as context, but the full calendar is its own workspace with drag-and-drop, filters, and multi-platform visibility.

### 11.5 Theme-Centric vs Free-Floating Posts

**Decision:** Posts can exist without a theme, but themes are encouraged.

**Why:** Themes provide: (a) LLM context for consistent voice, (b) scheduling cadence, (c) visual grouping in calendar, (d) progress tracking. But forcing every quick one-off post into a theme creates friction. Solution: "Quick Post" (no theme) is a valid path, with a nudge to assign a theme later.

---

## 12. Phase Plan (Frontend Only)

### Phase F1: Core Shell + Calendar + Text Posts (2 weeks)

- Layout shell: sidebar, routing, slide-over panel
- Dashboard page (stats + upcoming — read-only)
- Calendar page (week view, post cards, click to open editor)
- Post editor: Content tab (text only — static and generated modes)
- Post list with status badges
- Telegram variant (auto-adapted, read-only preview)
- API integration: posts CRUD, generate-text, approve, publish

### Phase F2: Themes + Image + Platform Variants (2 weeks)

- Themes page: list + detail
- Theme creation/editing
- Image section in post editor (upload + generate)
- Platforms tab in post editor (Telegram + Instagram variants)
- Calendar: drag-and-drop rescheduling
- Calendar: month view
- Content Library page (basic asset grid + upload)

### Phase F3: Video + Multi-Platform + Polish (2 weeks)

- Video section in post editor (script + generate)
- YouTube Short and Instagram Reel variants
- Channel pages (filtered views + settings)
- Batch generation modal
- History tab in post editor
- Dashboard: attention cards, active themes
- Real-time status updates (polling → WebSocket prep)

### Phase F4: Analytics + Refinement (1 week)

- Post analytics (engagement metrics pulled from platform APIs)
- Theme analytics (series performance)
- Calendar: list view
- Recurring post support
- Settings page: accounts, API keys, brand profile
- Mobile responsiveness pass

---

## 13. Backend API Additions Required

The existing Phase 1 backend (bot + workers + publishers) needs a FastAPI layer added as a new service. Key additions:

1. **`src/api/`** — FastAPI app with all endpoints from Section 7
2. **Auth middleware** — JWT or session-based (even simple API key for solo use)
3. **Generation jobs** — extend Redis queue to track job status for polling
4. **Theme model** — new database table (not in current schema)
5. **PlatformVariant as first-class entity** — extend `post_publications` or create new table
6. **Media asset storage** — S3-compatible (Scaleway Object Storage) for uploaded/generated files
7. **Calendar query** — optimized endpoint that returns posts in a date range grouped by day

The FastAPI service runs alongside the bot and workers in Docker Compose — same database, same Redis.
