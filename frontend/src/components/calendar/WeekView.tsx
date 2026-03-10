import { format } from "date-fns";

import { DayColumn } from "@/components/calendar/DayColumn";
import { Skeleton } from "@/components/ui/skeleton";
import { useCalendar } from "@/hooks/useCalendar";
import { useUIStore } from "@/stores/ui";
import { getWeekDays } from "@/lib/date";
import type { Post } from "@/lib/types";

function WeekViewSkeleton() {
  return (
    <div className="grid grid-cols-7 gap-2">
      {Array.from({ length: 7 }).map((_, i) => (
        <div key={i} className="flex flex-col gap-2 rounded-xl border border-border bg-card p-2">
          <Skeleton className="h-6 w-full rounded-md" />
          <Skeleton className="h-12 w-full rounded-md" />
          <Skeleton className="h-10 w-full rounded-md opacity-50" />
        </div>
      ))}
    </div>
  );
}

export function WeekView() {
  const { calendarDate, filters } = useUIStore();
  const weekDays = getWeekDays(calendarDate);

  const startISO = format(weekDays[0], "yyyy-MM-dd");
  const endISO = format(weekDays[weekDays.length - 1], "yyyy-MM-dd");

  const { data: calendarDays, isLoading, isError } = useCalendar(startISO, endISO);

  if (isLoading) return <WeekViewSkeleton />;

  if (isError) {
    return (
      <p className="rounded-xl border border-border bg-card px-4 py-6 text-center text-sm text-destructive">
        Failed to load calendar data. Please try again.
      </p>
    );
  }

  // Build a map: ISO date string -> Post[]
  const postsByDate = new Map<string, Post[]>();
  for (const day of calendarDays ?? []) {
    let posts = day.posts;

    // Apply filters
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

  return (
    <div
      className="grid gap-2"
      style={{ gridTemplateColumns: "repeat(7, minmax(0, 1fr))" }}
      role="grid"
      aria-label="Weekly calendar"
    >
      {weekDays.map((day) => {
        const key = format(day, "yyyy-MM-dd");
        const posts = postsByDate.get(key) ?? [];

        return (
          <DayColumn
            key={key}
            date={day}
            posts={posts}
          />
        );
      })}
    </div>
  );
}
