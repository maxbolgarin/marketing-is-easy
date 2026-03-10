export type UUID = string;

export type PostStatus =
  | "draft"
  | "generating"
  | "review"
  | "approved"
  | "publishing"
  | "published"
  | "failed"
  | "rejected";

export type Platform =
  | "telegram"
  | "instagram_post"
  | "instagram_reel"
  | "youtube_short"
  | "twitter";

export type ThemeStatus = "active" | "paused" | "completed" | "draft";

export type PostType = "text" | "image" | "video" | "carousel";

export type MediaType = "none" | "image" | "video" | "carousel";

export interface Publication {
  id: UUID;
  post_id: UUID;
  platform: Platform;
  platform_text?: string;
  platform_media_url?: string;
  status: PostStatus;
  published_at?: string;
  platform_post_id?: string;
  platform_url?: string;
  error_message?: string;
  retry_count: number;
  created_at: string;
}

export interface Theme {
  id: UUID;
  name: string;
  description?: string;
  status: ThemeStatus;
  target_platforms: Platform[];
  cadence_type: string;
  cadence_rule: string;
  start_date?: string;
  end_date?: string;
  generation_context?: string;
  default_prompt_template?: string;
  color: string;
  template_id?: UUID;
  track: string;
  created_at: string;
  updated_at: string;
  post_count: number;
  published_count: number;
  next_publish_at?: string;
}

export interface Post {
  id: UUID;
  source_id?: UUID;
  theme_id?: UUID;
  track: string;
  language: string;
  post_type: PostType;
  text_content?: string;
  text_prompt?: string;
  text_model?: string;
  media_type?: MediaType;
  media_urls?: string[];
  media_metadata: Record<string, unknown>;
  scheduled_at?: string;
  status: PostStatus;
  generation_params: Record<string, unknown>;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
  publications?: Publication[];
  theme?: Theme;
}

export interface CalendarDay {
  date: string;
  posts: Post[];
}

export interface DashboardStats {
  scheduled_this_week: number;
  pending_review: number;
  published_this_month: number;
  failed: number;
}

export interface Channel {
  id: UUID;
  track: string;
  platform: Platform;
  account_name?: string;
  config: Record<string, unknown>;
  is_active: boolean;
  token_expires_at?: string;
  created_at: string;
}

export interface Asset {
  id: UUID;
  path: string;
  url: string;
  filename: string;
  content_type: string;
  size: number;
  created_at: string;
}

export interface User {
  id: UUID;
  username: string;
  email?: string;
  is_active: boolean;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}
