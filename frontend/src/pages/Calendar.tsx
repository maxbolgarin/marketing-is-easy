import { CalendarToolbar } from "@/components/calendar/CalendarToolbar";
import { WeekView } from "@/components/calendar/WeekView";
import { useUIStore } from "@/stores/ui";

function MonthViewPlaceholder() {
  return (
    <div className="flex items-center justify-center rounded-xl border border-dashed border-border py-20 text-sm text-muted-foreground">
      Month view — coming soon
    </div>
  );
}

function ListViewPlaceholder() {
  return (
    <div className="flex items-center justify-center rounded-xl border border-dashed border-border py-20 text-sm text-muted-foreground">
      List view — coming soon
    </div>
  );
}

export default function Calendar() {
  const calendarView = useUIStore((s) => s.calendarView);

  return (
    <main className="flex flex-col gap-4 p-4 sm:p-6 lg:p-8">
      {/* Page header */}
      <header>
        <h1 className="text-xl font-semibold tracking-tight text-foreground">Calendar</h1>
        <p className="text-sm text-muted-foreground">Schedule and manage your posts</p>
      </header>

      {/* Toolbar: navigation + view switcher + filters */}
      <CalendarToolbar />

      {/* View content */}
      <div className="min-h-0 flex-1">
        {calendarView === "week" && <WeekView />}
        {calendarView === "month" && <MonthViewPlaceholder />}
        {calendarView === "list" && <ListViewPlaceholder />}
      </div>
    </main>
  );
}
