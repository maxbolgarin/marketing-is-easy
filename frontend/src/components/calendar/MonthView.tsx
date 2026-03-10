import { format, isSameMonth, isToday } from "date-fns";

import { Skeleton } from "@/components/ui/skeleton";
import { StatusDot } from "@/components/shared/StatusBadge";
import { useCalendar } from "@/hooks/useCalendar";
import { useUIStore } from "@/stores/ui";
import { useEditorStore } from "@/stores/editor";
import { getMonthDays } from "@/lib/date";
import type { Post } from "@/lib/types";
import { cn } from "@/lib/utils";

const DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function MonthViewSkeleton() {
  return (
    <div className="grid grid-cols-7 gap-px bg-border rounded-xl overflow-hidden">
      {Array.from({ length: 35 }).map((_, i) => (
        <div key={i} className="bg-card p-2 min-h-[80px]">
          <Skeleton className="h-4 w-6 rounded" />
        </div>
      ))}
    </div>
  );
}

export function MonthView() {
  const { calendarDate, filters, setCalendarDate, setCalendarView } = useUIStore();
  const openEditor = useEditorStore((s) => s.openEditor);
  const days = getMonthDays(calendarDate);

  const startISO = format(days[0], "yyyy-MM-dd");
  const endISO = format(days[days.length - 1], "yyyy-MM-dd");

  const { data: calendarDays, isLoading, isError } = useCalendar(startISO, endISO);

  if (isLoading) return <MonthViewSkeleton />;

  if (isError) {
    return (
      <p className="rounded-xl border border-border bg-card px-4 py-6 text-center text-sm text-destructive">
        Failed to load calendar data.
      </p>
    );
  }

  // Build date → posts map with filters
  const postsByDate = new Map<string, Post[]>();
  for (const day of calendarDays ?? []) {
    let posts = day.posts;

    if (filters.themes.length > 0) {
      posts = posts.filter((p) => p.theme_id && filters.themes.includes(p.theme_id));
    }
    if (filters.platforms.length > 0) {
      posts = posts.filter((p) =>
        p.publications?.some((pub) => filters.platforms.includes(pub.platform)),
      );
    }
    if (filters.statuses.length > 0) {
      posts = posts.filter((p) => filters.statuses.includes(p.status));
    }

    postsByDate.set(day.date, posts);
  }

  function handleDayClick(day: Date) {
    setCalendarDate(day);
    setCalendarView("week");
  }

  return (
    <div className="flex flex-col gap-0">
      {/* Day name headers */}
      <div className="grid grid-cols-7 gap-px mb-px">
        {DAY_NAMES.map((name) => (
          <div
            key={name}
            className="text-center text-[11px] font-medium uppercase tracking-wider text-muted-foreground py-1.5"
          >
            {name}
          </div>
        ))}
      </div>

      {/* Day cells */}
      <div className="grid grid-cols-7 gap-px bg-border rounded-xl overflow-hidden">
        {days.map((day) => {
          const key = format(day, "yyyy-MM-dd");
          const posts = postsByDate.get(key) ?? [];
          const today = isToday(day);
          const inMonth = isSameMonth(day, calendarDate);

          return (
            <div
              key={key}
              className={cn(
                "bg-card min-h-[80px] p-1.5 flex flex-col gap-1 cursor-pointer transition-colors hover:bg-accent/30",
                !inMonth && "opacity-40",
                today && "bg-primary/5",
              )}
              onClick={() => handleDayClick(day)}
            >
              <span
                className={cn(
                  "text-xs font-medium self-end w-6 h-6 flex items-center justify-center rounded-full",
                  today && "bg-primary text-primary-foreground",
                  !today && "text-muted-foreground",
                )}
              >
                {format(day, "d")}
              </span>

              {/* Post indicators */}
              <div className="flex flex-col gap-0.5 flex-1 min-h-0 overflow-hidden">
                {posts.slice(0, 3).map((post) => (
                  <button
                    key={post.id}
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      openEditor(post.id);
                    }}
                    className={cn(
                      "flex items-center gap-1 rounded px-1 py-0.5 text-left",
                      "hover:bg-accent transition-colors",
                      "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
                    )}
                    style={{
                      borderLeft: post.theme?.color
                        ? `2px solid ${post.theme.color}`
                        : undefined,
                    }}
                  >
                    <StatusDot status={post.status} className="shrink-0" />
                    <span className="text-[10px] truncate text-foreground leading-tight">
                      {(post.text_content ?? "").slice(0, 20) || "Draft"}
                    </span>
                  </button>
                ))}
                {posts.length > 3 && (
                  <span className="text-[10px] text-muted-foreground px-1">
                    +{posts.length - 3} more
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
