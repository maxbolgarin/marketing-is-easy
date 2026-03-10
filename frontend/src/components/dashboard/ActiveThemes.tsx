import { Link } from "react-router";
import { Layers } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { PlatformIcon } from "@/components/common/PlatformIcon";
import { useThemes } from "@/hooks/useTheme";
import type { Theme } from "@/lib/types";
import { cn } from "@/lib/utils";

function ThemeProgressBar({ value, max }: { value: number; max: number }) {
  const pct = max > 0 ? Math.min(100, Math.round((value / max) * 100)) : 0;
  return (
    <div className="h-1 w-full overflow-hidden rounded-full bg-muted" role="progressbar" aria-valuenow={value} aria-valuemax={max}>
      <div
        className="h-full rounded-full bg-primary transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

function ThemeRow({ theme }: { theme: Theme }) {
  return (
    <Link
      to={`/themes/${theme.id}`}
      className={cn(
        "group flex items-center gap-3 rounded-lg px-3 py-2.5 transition-colors",
        "hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
      )}
    >
      {/* Color dot */}
      <span
        className="size-2.5 shrink-0 rounded-full"
        style={{ backgroundColor: theme.color }}
        aria-hidden="true"
      />

      {/* Name + progress */}
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <p className="truncate text-sm font-medium group-hover:text-foreground">
            {theme.name}
          </p>
          <span className="shrink-0 text-xs text-muted-foreground tabular-nums">
            {theme.published_count}/{theme.post_count}
          </span>
        </div>
        <ThemeProgressBar value={theme.published_count} max={theme.post_count} />
      </div>

      {/* Platform icons */}
      {theme.target_platforms.length > 0 && (
        <div className="flex shrink-0 items-center gap-1">
          {theme.target_platforms.map((platform) => (
            <PlatformIcon key={platform} platform={platform} size={12} />
          ))}
        </div>
      )}
    </Link>
  );
}

function ActiveThemesSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-4 w-28" />
      </CardHeader>
      <CardContent className="flex flex-col gap-2">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3 px-1 py-2">
            <Skeleton className="size-2.5 rounded-full" />
            <div className="flex-1 space-y-1.5">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-1 w-full" />
            </div>
            <Skeleton className="h-3 w-8" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export function ActiveThemes() {
  const { data, isLoading, isError } = useThemes({ status: "active" });

  if (isLoading) return <ActiveThemesSkeleton />;

  if (isError) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Active Themes</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-destructive">Failed to load themes.</p>
        </CardContent>
      </Card>
    );
  }

  const themes = data?.items ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Layers className="size-4" />
          Active Themes
          {themes.length > 0 && (
            <span className="ml-1 text-xs font-normal text-muted-foreground">
              ({themes.length})
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="px-1">
        {themes.length === 0 ? (
          <EmptyState
            icon={Layers}
            title="No active themes"
            description="Create a theme to start generating content."
          />
        ) : (
          <ul role="list" className="flex flex-col">
            {themes.map((theme) => (
              <li key={theme.id}>
                <ThemeRow theme={theme} />
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
