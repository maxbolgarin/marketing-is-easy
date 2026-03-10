import { useEffect } from "react";
import { useSearchParams } from "react-router";

import { CalendarToolbar } from "@/components/calendar/CalendarToolbar";
import { MonthView } from "@/components/calendar/MonthView";
import { PostsList } from "@/components/calendar/PostsList";
import { WeekView } from "@/components/calendar/WeekView";
import { useUIStore } from "@/stores/ui";

export default function Calendar() {
  const calendarView = useUIStore((s) => s.calendarView);
  const setFilters = useUIStore((s) => s.setFilters);
  const [searchParams] = useSearchParams();

  // Apply URL query params as filters on mount
  useEffect(() => {
    const statusParam = searchParams.get("status");
    if (statusParam) {
      setFilters({ statuses: [statusParam] });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <main className="flex flex-col gap-4 p-4 sm:p-6 lg:p-8 h-full">
      {/* Page header */}
      <header>
        <h1 className="text-xl font-semibold tracking-tight text-foreground">Calendar</h1>
        <p className="text-sm text-muted-foreground">Schedule and manage your posts</p>
      </header>

      {/* Toolbar: navigation + view switcher + filters */}
      <CalendarToolbar />

      {/* Two-panel layout: posts list + calendar grid */}
      <div className="flex gap-4 min-h-0 flex-1">
        {/* Left: all posts list */}
        <aside className="w-72 shrink-0 flex flex-col min-h-0">
          <PostsList />
        </aside>

        {/* Right: calendar grid */}
        <div className="flex-1 min-w-0">
          {calendarView === "week" && <WeekView />}
          {calendarView === "month" && <MonthView />}
        </div>
      </div>
    </main>
  );
}
