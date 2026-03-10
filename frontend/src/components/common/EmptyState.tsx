import type { LucideIcon } from "lucide-react";
import { InboxIcon } from "lucide-react";

interface EmptyStateProps {
  icon?: LucideIcon;
  title?: string;
  description?: string;
}

export function EmptyState({
  icon: Icon = InboxIcon,
  title = "Nothing here yet",
  description,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-10 text-center text-muted-foreground">
      <Icon className="size-8 opacity-40" />
      <p className="text-sm font-medium">{title}</p>
      {description && <p className="max-w-xs text-xs opacity-70">{description}</p>}
    </div>
  );
}
