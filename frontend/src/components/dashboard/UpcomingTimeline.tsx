import { Clock } from "lucide-react";

import { PlatformIcon } from "@/components/shared/PlatformIcon";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { EmptyState } from "@/components/shared/EmptyState";
import { Skeleton } from "@/components/ui/skeleton";
import { useUpcoming } from "@/hooks/useDashboard";
import { useEditorStore } from "@/stores/editor";
import { formatTime } from "@/lib/date";
import type { Post } from "@/lib/types";
import { cn } from "@/lib/utils";

function TimelinePostItem({ post }: { post: Post }) {
  const openEditor = useEditorStore((s) => s.openEditor);

  const platforms = post.publications?.map((p) => p.platform) ?? [];
  const uniquePlatforms = [...new Set(platforms)];
  const preview = (post.text_content ?? "").slice(0, 30) + ((post.text_content?.length ?? 0) > 30 ? "…" : "");
  const time = post.scheduled_at ? formatTime(post.scheduled_at) : "--:--";

  return (
    <button
      type="button"
      onClick={() => openEditor(post.id)}
      className={cn(
        "flex shrink-0 flex-col gap-1.5 rounded-lg border border-border bg-card px-3 py-2.5",
        "min-w-[160px] max-w-[200px] text-left",
        "transition-colors hover:bg-accent hover:border-accent-foreground/20",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
      )}
    >
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Clock className="size-3 shrink-0" />
        <span className="font-mono">{time}</span>
      </div>

      {uniquePlatforms.length > 0 && (
        <div className="flex items-center gap-1">
          {uniquePlatforms.map((platform) => (
            <PlatformIcon key={platform} platform={platform} size={12} />
          ))}
        </div>
      )}

      <p className="line-clamp-2 text-xs text-foreground leading-snug">
        {preview || <span className="italic text-muted-foreground">No content</span>}
      </p>

      <StatusBadge status={post.status} />
    </button>
  );
}

function TimelineSkeletonItem() {
  return (
    <div className="flex shrink-0 flex-col gap-2 rounded-lg border border-border bg-card px-3 py-2.5 min-w-[160px]">
      <Skeleton className="h-3 w-12" />
      <Skeleton className="h-3 w-8" />
      <Skeleton className="h-6 w-full" />
      <Skeleton className="h-4 w-14" />
    </div>
  );
}

export function UpcomingTimeline() {
  const { data, isLoading, isError } = useUpcoming();

  return (
    <section aria-label="Upcoming posts in the next 48 hours">
      <h2 className="mb-3 text-sm font-semibold text-foreground">Next 48h</h2>

      {isLoading ? (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {Array.from({ length: 6 }).map((_, i) => (
            <TimelineSkeletonItem key={i} />
          ))}
        </div>
      ) : isError ? (
        <p className="text-xs text-destructive">Failed to load upcoming posts.</p>
      ) : !data?.posts.length ? (
        <div className="rounded-xl border border-border bg-card">
          <EmptyState
            icon={Clock}
            title="No posts scheduled in the next 48 hours"
          />
        </div>
      ) : (
        <div
          className="flex gap-2 overflow-x-auto pb-1"
          role="list"
          aria-label="Upcoming posts"
        >
          {data.posts.map((post) => (
            <div key={post.id} role="listitem">
              <TimelinePostItem post={post} />
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
