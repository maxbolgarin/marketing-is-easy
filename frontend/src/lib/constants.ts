import type { Platform, PostStatus } from "@/lib/types";

export const PLATFORM_COLORS: Record<Platform, string> = {
  telegram: "#2AABEE",
  instagram_post: "#E4405F",
  instagram_reel: "#E4405F",
  youtube_short: "#FF0000",
  twitter: "#1DA1F2",
};

export const PLATFORM_LABELS: Record<Platform, string> = {
  telegram: "Telegram",
  instagram_post: "Instagram Post",
  instagram_reel: "Instagram Reel",
  youtube_short: "YouTube Short",
  twitter: "Twitter",
};

export const PLATFORM_CHAR_LIMITS: Record<Platform, number> = {
  telegram: 4096,
  instagram_post: 2200,
  instagram_reel: 2200,
  youtube_short: 5000,
  twitter: 280,
};

export const STATUS_COLORS: Record<PostStatus, string> = {
  draft: "gray",
  generating: "blue",
  review: "yellow",
  approved: "green",
  publishing: "blue",
  published: "emerald",
  failed: "red",
  rejected: "gray",
};

export const STATUS_LABELS: Record<PostStatus, string> = {
  draft: "Draft",
  generating: "Generating",
  review: "Review",
  approved: "Approved",
  publishing: "Publishing",
  published: "Published",
  failed: "Failed",
  rejected: "Rejected",
};
