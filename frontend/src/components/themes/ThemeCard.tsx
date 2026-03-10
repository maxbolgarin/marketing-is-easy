import { Link } from "react-router";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import PlatformIcon from "@/components/shared/PlatformIcon";
import { PLATFORM_LABELS } from "@/lib/constants";
import type { Theme, ThemeStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const THEME_STATUS_STYLES: Record<ThemeStatus, string> = {
  active: "bg-emerald-950 text-emerald-400",
  paused: "bg-yellow-950 text-yellow-400",
  completed: "bg-muted text-muted-foreground",
  draft: "border-zinc-500 text-zinc-400",
};

interface ThemeCardProps {
  theme: Theme;
}

export default function ThemeCard({ theme }: ThemeCardProps) {
  const progress =
    theme.post_count > 0
      ? Math.round((theme.published_count / theme.post_count) * 100)
      : 0;

  return (
    <Link
      to={`/themes/${theme.id}`}
      className="block outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-xl"
    >
      <Card className="h-full transition-colors hover:ring-foreground/20 cursor-pointer">
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <span
                className="size-3 rounded-full shrink-0 ring-1 ring-white/10"
                style={{ backgroundColor: theme.color || "#52525b" }}
              />
              <CardTitle className="truncate">{theme.name}</CardTitle>
            </div>
            <Badge
              variant={theme.status === "draft" ? "outline" : "secondary"}
              className={cn("shrink-0 capitalize", THEME_STATUS_STYLES[theme.status])}
            >
              {theme.status}
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="flex flex-col gap-3">
          {theme.description && (
            <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
              {theme.description}
            </p>
          )}

          {/* Platform icons */}
          {theme.target_platforms.length > 0 && (
            <div className="flex items-center gap-1.5 flex-wrap">
              {theme.target_platforms.map((p) => (
                <div
                  key={p}
                  className="flex items-center gap-1 rounded-md bg-muted/50 px-1.5 py-0.5"
                  title={PLATFORM_LABELS[p]}
                >
                  <PlatformIcon platform={p} className="size-3" />
                  <span className="text-[10px] text-muted-foreground">
                    {PLATFORM_LABELS[p]}
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Progress bar */}
          {theme.post_count > 0 && (
            <div className="flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-muted-foreground">
                  {theme.published_count} / {theme.post_count} posts published
                </span>
                <span className="text-xs text-muted-foreground">{progress}%</span>
              </div>
              <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {theme.post_count === 0 && (
            <p className="text-xs text-muted-foreground italic">No posts yet</p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
