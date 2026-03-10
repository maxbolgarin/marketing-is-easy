import { useState } from "react";
import { CalendarClock } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useUpdatePost } from "@/hooks/usePost";
import { formatDateTime } from "@/lib/date";
import type { Post } from "@/lib/types";

interface ScheduleTabProps {
  post: Post;
}

function toLocalDatetimeString(isoString: string): string {
  const date = new Date(isoString);
  const offset = date.getTimezoneOffset() * 60000;
  const local = new Date(date.getTime() - offset);
  return local.toISOString().slice(0, 16);
}

function toISOString(localDatetime: string): string {
  return new Date(localDatetime).toISOString();
}

export default function ScheduleTab({ post }: ScheduleTabProps) {
  const [scheduledAt, setScheduledAt] = useState<string>(
    post.scheduled_at ? toLocalDatetimeString(post.scheduled_at) : "",
  );

  const updatePost = useUpdatePost();
  const isPending = updatePost.isPending;

  function handleSchedule() {
    if (!scheduledAt) return;
    updatePost.mutate({
      id: post.id,
      data: { scheduled_at: toISOString(scheduledAt) },
    });
  }

  function handleClear() {
    setScheduledAt("");
    updatePost.mutate({
      id: post.id,
      data: { scheduled_at: undefined },
    });
  }

  return (
    <div className="flex flex-col gap-5">
      {post.scheduled_at && (
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card px-4 py-3">
          <CalendarClock className="size-4 text-muted-foreground shrink-0" />
          <div className="flex flex-col gap-0.5">
            <p className="text-xs text-muted-foreground">Currently scheduled</p>
            <p className="text-sm font-medium">
              {formatDateTime(post.scheduled_at)}
            </p>
          </div>
          <Button
            variant="ghost"
            size="xs"
            className="ml-auto text-muted-foreground hover:text-foreground"
            onClick={handleClear}
            disabled={isPending}
          >
            Clear
          </Button>
        </div>
      )}

      <div className="flex flex-col gap-2">
        <label
          htmlFor="schedule-datetime"
          className="text-xs font-medium text-muted-foreground uppercase tracking-wide"
        >
          Schedule Date & Time
        </label>
        <input
          id="schedule-datetime"
          type="datetime-local"
          value={scheduledAt}
          onChange={(e) => setScheduledAt(e.target.value)}
          className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm shadow-xs transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 [color-scheme:dark]"
        />
      </div>

      <Button
        size="sm"
        disabled={!scheduledAt || isPending}
        onClick={handleSchedule}
        className="self-start gap-1.5"
      >
        <CalendarClock className="size-3.5" />
        {post.scheduled_at ? "Reschedule" : "Schedule"}
      </Button>
    </div>
  );
}
