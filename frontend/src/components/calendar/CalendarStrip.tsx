import { format, isToday, parseISO } from "date-fns";

import { StatusDot } from "@/components/shared/StatusBadge";
import { getWeekDays } from "@/lib/date";
import type { Post } from "@/lib/types";
import { cn } from "@/lib/utils";

interface CalendarStripProps {
  posts: Post[];
  start?: Date;
}

export function CalendarStrip({ posts, start = new Date() }: CalendarStripProps) {
  const weekDays = getWeekDays(start);

  // Group posts by date string
  const postsByDate = new Map<string, Post[]>();
  for (const day of weekDays) {
    postsByDate.set(format(day, "yyyy-MM-dd"), []);
  }
  for (const post of posts) {
    if (!post.scheduled_at) continue;
    const key = format(parseISO(post.scheduled_at), "yyyy-MM-dd");
    const existing = postsByDate.get(key);
    if (existing) existing.push(post);
  }

  return (
    <div
      className="grid grid-cols-7 gap-1"
      role="grid"
      aria-label="Weekly post summary"
    >
      {weekDays.map((day) => {
        const key = format(day, "yyyy-MM-dd");
        const dayPosts = postsByDate.get(key) ?? [];
        const today = isToday(day);

        return (
          <div
            key={key}
            role="gridcell"
            className="flex flex-col items-center gap-1 py-1.5"
          >
            {/* Day label */}
            <span
              className={cn(
                "text-[10px] font-medium uppercase tracking-wider",
                today ? "text-primary" : "text-muted-foreground",
              )}
            >
              {format(day, "EEE")}
            </span>

            {/* Date number */}
            <span
              className={cn(
                "flex size-5 items-center justify-center rounded-full text-[11px] font-semibold",
                today ? "bg-primary text-primary-foreground" : "text-foreground",
              )}
            >
              {format(day, "d")}
            </span>

            {/* Status dots for posts */}
            <div className="flex flex-wrap items-center justify-center gap-0.5 min-h-[10px]">
              {dayPosts.slice(0, 5).map((post) => (
                <StatusDot key={post.id} status={post.status} className="size-1.5" />
              ))}
              {dayPosts.length > 5 && (
                <span className="text-[9px] text-muted-foreground">+{dayPosts.length - 5}</span>
              )}
            </div>

            {/* Post count */}
            {dayPosts.length > 0 && (
              <span className="text-[9px] text-muted-foreground">{dayPosts.length}</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
