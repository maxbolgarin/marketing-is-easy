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

      {/* Stacked layout: calendar grid on top, posts list below */}
      <div className="flex flex-col gap-4 min-h-0 flex-1">
        {/* Calendar grid — full width */}
        <div className="w-full">
          {calendarView === "week" && <WeekView />}
          {calendarView === "month" && <MonthView />}
        </div>

        {/* Posts list — full width, scrollable */}
        <div className="flex-1 min-h-0">
          <PostsList />
        </div>
      </div>
    </main>
  );
}
