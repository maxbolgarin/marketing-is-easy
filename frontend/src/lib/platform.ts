import type { Platform } from "@/lib/types";

export interface PlatformConfig {
  /** Maximum character count for post text */
  charLimit: number;
  /** Preferred aspect ratio for media (width:height) */
  aspectRatio: string;
  /** Aspect ratio as a decimal (width / height) */
  aspectRatioDecimal: number;
  /** Whether hashtags are supported */
  hashtagsSupported: boolean;
  /** Recommended maximum number of hashtags (0 = no limit) */
  maxHashtags: number;
  /** Whether hashtags should appear in-text or appended at the end */
  hashtagPlacement: "inline" | "appended" | "none";
  /** Whether media is required */
  mediaRequired: boolean;
  /** Accepted media types */
  acceptedMediaTypes: Array<"image" | "video" | "carousel">;
  /** Maximum video duration in seconds (0 = no video) */
  maxVideoDurationSeconds: number;
  /** Maximum image size in MB */
  maxImageSizeMB: number;
  /** Recommended image resolution (WxH) */
  recommendedResolution?: string;
}

export const PLATFORM_CONFIG: Record<Platform, PlatformConfig> = {
  telegram: {
    charLimit: 4096,
    aspectRatio: "1:1",
    aspectRatioDecimal: 1,
    hashtagsSupported: true,
    maxHashtags: 0,
    hashtagPlacement: "inline",
    mediaRequired: false,
    acceptedMediaTypes: ["image", "video"],
    maxVideoDurationSeconds: 0,
    maxImageSizeMB: 10,
    recommendedResolution: "1280x720",
  },

  instagram_post: {
    charLimit: 2200,
    aspectRatio: "1:1",
    aspectRatioDecimal: 1,
    hashtagsSupported: true,
    maxHashtags: 30,
    hashtagPlacement: "appended",
    mediaRequired: true,
    acceptedMediaTypes: ["image", "carousel"],
    maxVideoDurationSeconds: 0,
    maxImageSizeMB: 8,
    recommendedResolution: "1080x1080",
  },

  instagram_reel: {
    charLimit: 2200,
    aspectRatio: "9:16",
    aspectRatioDecimal: 9 / 16,
    hashtagsSupported: true,
    maxHashtags: 30,
    hashtagPlacement: "appended",
    mediaRequired: true,
    acceptedMediaTypes: ["video"],
    maxVideoDurationSeconds: 90,
    maxImageSizeMB: 0,
    recommendedResolution: "1080x1920",
  },

  youtube_short: {
    charLimit: 5000,
    aspectRatio: "9:16",
    aspectRatioDecimal: 9 / 16,
    hashtagsSupported: true,
    maxHashtags: 15,
    hashtagPlacement: "appended",
    mediaRequired: true,
    acceptedMediaTypes: ["video"],
    maxVideoDurationSeconds: 60,
    maxImageSizeMB: 0,
    recommendedResolution: "1080x1920",
  },

  twitter: {
    charLimit: 280,
    aspectRatio: "16:9",
    aspectRatioDecimal: 16 / 9,
    hashtagsSupported: true,
    maxHashtags: 2,
    hashtagPlacement: "inline",
    mediaRequired: false,
    acceptedMediaTypes: ["image", "video"],
    maxVideoDurationSeconds: 140,
    maxImageSizeMB: 5,
    recommendedResolution: "1200x675",
  },
};
