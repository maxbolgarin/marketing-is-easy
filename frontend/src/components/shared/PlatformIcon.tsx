import { cn } from "@/lib/utils";
import { PLATFORM_COLORS } from "@/lib/constants";
import type { Platform } from "@/lib/types";
import {
  Send,
  Instagram,
  Youtube,
  Twitter,
  Mail,
  HelpCircle,
} from "lucide-react";

interface PlatformIconProps {
  platform: string;
  className?: string;
  size?: number;
}

export function PlatformIcon({ platform, className, size }: PlatformIconProps) {
  const color =
    (PLATFORM_COLORS as Record<string, string>)[platform] ?? "#a1a1aa";

  const iconProps = {
    className: cn("size-4 shrink-0", className),
    style: { color },
    ...(size != null ? { size } : {}),
  };

  switch (platform as Platform | string) {
    case "telegram":
      return <Send {...iconProps} />;
    case "instagram_post":
    case "instagram_reel":
      return <Instagram {...iconProps} />;
    case "youtube_short":
      return <Youtube {...iconProps} />;
    case "twitter":
      return <Twitter {...iconProps} />;
    case "email":
      return <Mail {...iconProps} />;
    default:
      return <HelpCircle {...iconProps} />;
  }
}

export default PlatformIcon;
