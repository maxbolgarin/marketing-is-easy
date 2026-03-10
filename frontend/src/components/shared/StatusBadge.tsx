import { Badge } from "@/components/ui/badge";
import { STATUS_COLORS, STATUS_LABELS } from "@/lib/constants";
import type { PostStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: PostStatus;
}

const COLOR_CLASS_MAP: Record<string, { outline: string; secondary: string }> = {
  gray: {
    outline: "border-zinc-500 text-zinc-400",
    secondary: "bg-zinc-800 text-zinc-400",
  },
  blue: {
    outline: "border-blue-500 text-blue-400",
    secondary: "bg-blue-950 text-blue-400",
  },
  yellow: {
    outline: "border-yellow-500 text-yellow-400",
    secondary: "bg-yellow-950 text-yellow-400",
  },
  green: {
    outline: "border-green-500 text-green-400",
    secondary: "bg-green-950 text-green-400",
  },
  emerald: {
    outline: "border-emerald-500 text-emerald-400",
    secondary: "bg-emerald-950 text-emerald-400",
  },
  red: {
    outline: "border-red-500 text-red-400",
    secondary: "bg-red-950 text-red-400",
  },
};

const OUTLINE_STATUSES: PostStatus[] = ["draft", "rejected", "failed"];

export default function StatusBadge({ status }: StatusBadgeProps) {
  const color = STATUS_COLORS[status] ?? "gray";
  const colorClasses = COLOR_CLASS_MAP[color] ?? COLOR_CLASS_MAP.gray;
  const useOutline = OUTLINE_STATUSES.includes(status);

  return (
    <Badge
      variant={useOutline ? "outline" : "secondary"}
      className={cn(useOutline ? colorClasses.outline : colorClasses.secondary)}
    >
      {STATUS_LABELS[status]}
    </Badge>
  );
}
