import { PlatformIcon } from "@/components/common/PlatformIcon";
import { StatusDot } from "@/components/common/StatusBadge";
import { useEditorStore } from "@/stores/editor";
import { formatTime } from "@/lib/date";
import type { Post, Platform } from "@/lib/types";
import { cn } from "@/lib/utils";

interface CalendarPostCardProps {
  post: Post;
}

export function CalendarPostCard({ post }: CalendarPostCardProps) {
  const openEditor = useEditorStore((s) => s.openEditor);

  const platforms: Platform[] = [
    ...new Set(post.publications?.map((p) => p.platform) ?? []),
  ];

  const preview = (post.text_content ?? "").slice(0, 30) + ((post.text_content?.length ?? 0) > 30 ? "…" : "");
  const time = post.scheduled_at ? formatTime(post.scheduled_at) : "—";
  const themeColor = post.theme?.color;

  return (
    <button
      type="button"
      onClick={() => openEditor(post.id)}
      className={cn(
        "group relative w-full overflow-hidden rounded-md border border-border bg-card text-left",
        "transition-colors hover:bg-accent hover:border-accent-foreground/20",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        "pl-[3px]",
      )}
      aria-label={`Post: ${preview || "No content"} at ${time}`}
    >
      {/* Theme color left border accent */}
      {themeColor && (
        <span
          className="absolute inset-y-0 left-0 w-[3px] rounded-l-md"
          style={{ backgroundColor: themeColor }}
          aria-hidden="true"
        />
      )}

      <div className="flex flex-col gap-1 px-2 py-1.5">
        {/* Time row */}
        <div className="flex items-center justify-between gap-1">
          <span className="font-mono text-[10px] text-muted-foreground">{time}</span>
          <StatusDot status={post.status} />
        </div>

        {/* Preview text */}
        <p className="line-clamp-2 text-xs leading-snug text-foreground">
          {preview || <span className="italic text-muted-foreground">No content</span>}
        </p>

        {/* Platform icons */}
        {platforms.length > 0 && (
          <div className="flex items-center gap-0.5 mt-0.5">
            {platforms.map((platform) => (
              <PlatformIcon key={platform} platform={platform} size={10} />
            ))}
          </div>
        )}
      </div>
    </button>
  );
}
