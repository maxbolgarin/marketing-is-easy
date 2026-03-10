import { ChevronLeft, ChevronRight, Filter, X } from "lucide-react";
import { format, addWeeks, subWeeks } from "date-fns";

import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuCheckboxItem,
} from "@/components/ui/dropdown-menu";
import { useUIStore } from "@/stores/ui";
import { useThemes } from "@/hooks/useTheme";
import { PLATFORM_LABELS, STATUS_LABELS } from "@/lib/constants";
import type { Platform, PostStatus } from "@/lib/types";
import { getWeekDays } from "@/lib/date";
import { cn } from "@/lib/utils";

const PLATFORMS: Platform[] = [
  "telegram",
  "instagram_post",
  "instagram_reel",
  "youtube_short",
  "twitter",
];

const STATUSES: PostStatus[] = [
  "draft",
  "generating",
  "review",
  "approved",
  "publishing",
  "published",
  "failed",
  "rejected",
];

function WeekRangeLabel({ date }: { date: Date }) {
  const days = getWeekDays(date);
  const start = days[0];
  const end = days[days.length - 1];

  if (start.getMonth() === end.getMonth()) {
    return (
      <span className="text-sm font-medium tabular-nums">
        {format(start, "MMM d")} – {format(end, "d, yyyy")}
      </span>
    );
  }

  return (
    <span className="text-sm font-medium tabular-nums">
      {format(start, "MMM d")} – {format(end, "MMM d, yyyy")}
    </span>
  );
}

function FilterDropdown() {
  const { filters, setFilters, resetFilters } = useUIStore();
  const { data: themesData } = useThemes({ status: "active" });
  const themes = themesData?.items ?? [];

  const hasActiveFilters =
    filters.themes.length > 0 ||
    filters.platforms.length > 0 ||
    filters.statuses.length > 0;

  function toggleTheme(id: string) {
    const next = filters.themes.includes(id)
      ? filters.themes.filter((t) => t !== id)
      : [...filters.themes, id];
    setFilters({ themes: next });
  }

  function togglePlatform(platform: string) {
    const next = filters.platforms.includes(platform)
      ? filters.platforms.filter((p) => p !== platform)
      : [...filters.platforms, platform];
    setFilters({ platforms: next });
  }

  function toggleStatus(status: string) {
    const next = filters.statuses.includes(status)
      ? filters.statuses.filter((s) => s !== status)
      : [...filters.statuses, status];
    setFilters({ statuses: next });
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        render={
          <Button
            variant="outline"
            size="sm"
            className={cn(hasActiveFilters && "border-primary text-primary")}
          >
            <Filter className="size-3.5" />
            Filter
            {hasActiveFilters && (
              <span className="ml-1 flex size-4 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                {filters.themes.length + filters.platforms.length + filters.statuses.length}
              </span>
            )}
          </Button>
        }
      />
      <DropdownMenuContent side="bottom" align="end" className="min-w-[200px]">
        {themes.length > 0 && (
          <>
            <DropdownMenuLabel>Theme</DropdownMenuLabel>
            {themes.map((theme) => (
              <DropdownMenuCheckboxItem
                key={theme.id}
                checked={filters.themes.includes(theme.id)}
                onCheckedChange={() => toggleTheme(theme.id)}
              >
                <span
                  className="mr-2 inline-block size-2 rounded-full"
                  style={{ backgroundColor: theme.color }}
                />
                {theme.name}
              </DropdownMenuCheckboxItem>
            ))}
            <DropdownMenuSeparator />
          </>
        )}

        <DropdownMenuLabel>Platform</DropdownMenuLabel>
        {PLATFORMS.map((platform) => (
          <DropdownMenuCheckboxItem
            key={platform}
            checked={filters.platforms.includes(platform)}
            onCheckedChange={() => togglePlatform(platform)}
          >
            {PLATFORM_LABELS[platform]}
          </DropdownMenuCheckboxItem>
        ))}

        <DropdownMenuSeparator />

        <DropdownMenuLabel>Status</DropdownMenuLabel>
        {STATUSES.map((status) => (
          <DropdownMenuCheckboxItem
            key={status}
            checked={filters.statuses.includes(status)}
            onCheckedChange={() => toggleStatus(status)}
          >
            {STATUS_LABELS[status]}
          </DropdownMenuCheckboxItem>
        ))}

        {hasActiveFilters && (
          <>
            <DropdownMenuSeparator />
            <button
              type="button"
              onClick={resetFilters}
              className="flex w-full items-center gap-1.5 rounded-md px-1.5 py-1 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            >
              <X className="size-3.5" />
              Reset filters
            </button>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function CalendarToolbar() {
  const { calendarView, setCalendarView, calendarDate, setCalendarDate } = useUIStore();

  function gotoPrev() {
    setCalendarDate(subWeeks(calendarDate, 1));
  }

  function gotoNext() {
    setCalendarDate(addWeeks(calendarDate, 1));
  }

  function gotoToday() {
    setCalendarDate(new Date());
  }

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5">
      {/* Left: nav */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={gotoPrev}
          aria-label="Previous week"
        >
          <ChevronLeft className="size-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={gotoNext}
          aria-label="Next week"
        >
          <ChevronRight className="size-4" />
        </Button>
        <Button
          variant="ghost"
          size="xs"
          onClick={gotoToday}
          className="ml-1 text-xs"
        >
          Today
        </Button>
        <span className="ml-2 hidden sm:block">
          <WeekRangeLabel date={calendarDate} />
        </span>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Center: view toggle */}
      <Tabs value={calendarView} onValueChange={(v) => setCalendarView(v as typeof calendarView)}>
        <TabsList>
          <TabsTrigger value="week">Week</TabsTrigger>
          <TabsTrigger value="month">Month</TabsTrigger>
          <TabsTrigger value="list">List</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Right: filters */}
      <FilterDropdown />
    </div>
  );
}
