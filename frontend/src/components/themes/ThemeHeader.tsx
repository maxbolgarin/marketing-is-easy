import { Link } from "react-router";
import { ArrowLeft, Settings, Pencil, CalendarDays } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import PlatformIcon from "@/components/shared/PlatformIcon";
import { PLATFORM_LABELS } from "@/lib/constants";
import type { Theme, ThemeStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

function formatCadenceRule(rule: Record<string, unknown>): string {
  if (!rule || Object.keys(rule).length === 0) return "—";
  const freq = rule.frequency as string | undefined;
  const days = rule.days as string[] | undefined;
  const time = rule.time as string | undefined;
  const parts: string[] = [];
  if (freq) parts.push(freq);
  if (days?.length) parts.push(days.join(", "));
  if (time) parts.push(`at ${time}`);
  return parts.length > 0 ? parts.join(" • ") : JSON.stringify(rule);
}

const THEME_STATUS_STYLES: Record<ThemeStatus, string> = {
  active: "bg-emerald-950 text-emerald-400",
  paused: "bg-yellow-950 text-yellow-400",
  completed: "bg-muted text-muted-foreground",
  draft: "border-zinc-500 text-zinc-400",
};

interface ThemeHeaderProps {
  theme: Theme;
}

export default function ThemeHeader({ theme }: ThemeHeaderProps) {
  const progress =
    theme.post_count > 0
      ? Math.round((theme.published_count / theme.post_count) * 100)
      : 0;

  return (
    <div className="flex flex-col gap-4 pb-4 border-b border-border">
      <div className="flex items-center justify-between gap-2">
        <Link
          to="/themes"
          className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="size-4" />
          Themes
        </Link>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <Pencil className="size-3.5" />
            Edit
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Theme settings">
            <Settings className="size-4" />
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-3 flex-wrap">
          <span
            className="size-4 rounded-full ring-1 ring-white/10 shrink-0"
            style={{ backgroundColor: theme.color || "#52525b" }}
          />
          <h1 className="text-2xl font-bold tracking-tight">{theme.name}</h1>
          <Badge
            variant={theme.status === "draft" ? "outline" : "secondary"}
            className={cn("capitalize", THEME_STATUS_STYLES[theme.status])}
          >
            {theme.status}
          </Badge>
        </div>

        {theme.description && (
          <p className="text-sm text-muted-foreground leading-relaxed max-w-2xl">
            {theme.description}
          </p>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-4 text-sm">
        {/* Platforms */}
        {theme.target_platforms.length > 0 && (
          <div className="flex items-center gap-1.5">
            {theme.target_platforms.map((p) => (
              <div
                key={p}
                className="flex items-center gap-1 rounded-md bg-muted/50 px-2 py-1"
                title={PLATFORM_LABELS[p]}
              >
                <PlatformIcon platform={p} className="size-3.5" />
                <span className="text-xs text-muted-foreground">
                  {PLATFORM_LABELS[p]}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Cadence */}
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <CalendarDays className="size-3.5" />
          <span className="text-xs">
            {theme.cadence_type}: {formatCadenceRule(theme.cadence_rule ?? {})}
          </span>
        </div>
      </div>

      {/* Progress */}
      {theme.post_count > 0 && (
        <div className="flex flex-col gap-1 max-w-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              {theme.published_count} / {theme.post_count} posts published
            </span>
            <span className="text-xs text-muted-foreground font-medium">
              {progress}%
            </span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full rounded-full bg-primary transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
