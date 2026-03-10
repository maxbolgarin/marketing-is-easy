import { format, isToday, parseISO } from "date-fns";
import { Plus } from "lucide-react";

import { CalendarPostCard } from "@/components/calendar/CalendarPostCard";
import { useEditorStore } from "@/stores/editor";
import type { Post } from "@/lib/types";
import { cn } from "@/lib/utils";

interface DayColumnProps {
  date: Date;
  posts: Post[];
}

function sortByTime(a: Post, b: Post): number {
  const ta = a.scheduled_at ? parseISO(a.scheduled_at).getTime() : 0;
  const tb = b.scheduled_at ? parseISO(b.scheduled_at).getTime() : 0;
  return ta - tb;
}

export function DayColumn({ date, posts }: DayColumnProps) {
  const openEditor = useEditorStore((s) => s.openEditor);
  const today = isToday(date);
  const sorted = [...posts].sort(sortByTime);

  function handleEmptyClick() {
    openEditor("", date.toISOString());
  }

  return (
    <div
      className={cn(
        "flex min-w-0 flex-1 flex-col gap-1 rounded-xl border border-border bg-card",
        today && "border-primary/40 bg-primary/5",
      )}
    >
      {/* Day header */}
      <div
        className={cn(
          "flex items-center gap-1.5 rounded-t-xl border-b border-border px-2.5 py-2",
          today && "border-primary/30",
        )}
      >
        <span
          className={cn(
            "text-[11px] font-medium uppercase tracking-wider text-muted-foreground",
            today && "text-primary",
          )}
        >
          {format(date, "EEE")}
        </span>
        <span
          className={cn(
            "flex size-5 items-center justify-center rounded-full text-xs font-semibold",
            today
              ? "bg-primary text-primary-foreground"
              : "text-foreground",
          )}
        >
          {format(date, "d")}
        </span>
      </div>

      {/* Posts list */}
      <div className="flex flex-col gap-1 px-1.5 pb-1.5">
        {sorted.map((post) => (
          <CalendarPostCard key={post.id} post={post} />
        ))}

        {/* Empty area — click to create post */}
        <button
          type="button"
          onClick={handleEmptyClick}
          className={cn(
            "group flex w-full items-center justify-center gap-1 rounded-md py-1.5 text-xs text-muted-foreground/50",
            "hover:bg-muted/50 hover:text-muted-foreground transition-colors",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
            sorted.length === 0 && "py-4",
          )}
          aria-label={`Create post on ${format(date, "MMM d")}`}
        >
          <Plus className="size-3 opacity-0 transition-opacity group-hover:opacity-100" />
          {sorted.length === 0 && (
            <span className="opacity-0 transition-opacity group-hover:opacity-100 text-[10px]">
              Add post
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
