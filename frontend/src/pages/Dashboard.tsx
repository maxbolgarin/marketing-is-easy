import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { StatsRow } from "@/components/dashboard/StatsRow";
import { UpcomingTimeline } from "@/components/dashboard/UpcomingTimeline";
import { AttentionCards } from "@/components/dashboard/AttentionCards";
import { ActiveThemes } from "@/components/dashboard/ActiveThemes";
import { useEditorStore } from "@/stores/editor";

export default function Dashboard() {
  const openEditor = useEditorStore((s) => s.openEditor);

  function handleNewPost() {
    // Open editor with an empty string to signal "create new post"
    openEditor("");
  }

  return (
    <main className="flex flex-col gap-6 p-4 sm:p-6 lg:p-8">
      {/* Page header */}
      <header className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground">Dashboard</h1>
          <p className="text-sm text-muted-foreground">Overview of your social content</p>
        </div>
        <Button onClick={handleNewPost} size="sm">
          <Plus className="size-4" />
          New Post
        </Button>
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
