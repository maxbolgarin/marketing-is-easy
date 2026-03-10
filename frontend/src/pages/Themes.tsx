import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import ThemeCard from "@/components/themes/ThemeCard";
import { useThemes } from "@/hooks/useTheme";

export default function Themes() {
  const { data, isLoading, isError } = useThemes();
  const themes = data?.items ?? [];

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Themes</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Manage your content themes and campaigns.
          </p>
        </div>
        <Button size="sm" className="gap-1.5">
          <Plus className="size-3.5" />
          New Theme
        </Button>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-48 w-full rounded-xl" />
          ))}
        </div>
      )}

      {isError && (
        <div className="flex items-center justify-center py-20">
          <p className="text-sm text-muted-foreground">
            Failed to load themes. Please try again.
          </p>
        </div>
      )}

      {!isLoading && !isError && themes.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-3 py-20 text-muted-foreground">
          <p className="text-sm">No themes yet.</p>
          <Button size="sm" className="gap-1.5">
            <Plus className="size-3.5" />
            Create your first theme
          </Button>
        </div>
      )}

      {!isLoading && themes.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {themes.map((theme) => (
            <ThemeCard key={theme.id} theme={theme} />
          ))}
        </div>
      )}
    </div>
  );
}
