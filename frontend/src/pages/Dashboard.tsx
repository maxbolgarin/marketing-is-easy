import { StatsRow } from "@/components/dashboard/StatsRow";
import { UpcomingTimeline } from "@/components/dashboard/UpcomingTimeline";
import { AttentionCards } from "@/components/dashboard/AttentionCards";
import { ActiveThemes } from "@/components/dashboard/ActiveThemes";

export default function Dashboard() {
  return (
    <main className="flex flex-col gap-6 p-4 sm:p-6 lg:p-8">
      {/* Page header */}
      <header>
        <h1 className="text-xl font-semibold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Overview of your social content</p>
      </header>

      {/* Stats row */}
      <StatsRow />

      {/* Attention cards — only renders when there are items needing attention */}
      <AttentionCards />

      {/* Upcoming 48h timeline */}
      <UpcomingTimeline />

      {/* Active themes list */}
      <ActiveThemes />
    </main>
  );
}
