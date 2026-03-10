import { Badge } from "@/components/ui/badge";
import { STATUS_COLORS, STATUS_LABELS } from "@/lib/constants";
import type { PostStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: PostStatus;
  className?: string;
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

const STATUS_DOT_CLASSES: Record<PostStatus, string> = {
  draft: "bg-zinc-500",
  generating: "bg-blue-400",
  review: "bg-yellow-400",
  approved: "bg-green-400",
  publishing: "bg-blue-400",
  published: "bg-emerald-400",
  failed: "bg-red-400",
  rejected: "bg-zinc-500",
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const color = STATUS_COLORS[status] ?? "gray";
  const colorClasses = COLOR_CLASS_MAP[color] ?? COLOR_CLASS_MAP.gray;
  const useOutline = OUTLINE_STATUSES.includes(status);

  return (
    <Badge
      variant={useOutline ? "outline" : "secondary"}
      className={cn(useOutline ? colorClasses.outline : colorClasses.secondary, className)}
    >
      {STATUS_LABELS[status]}
    </Badge>
  );
}

export function StatusDot({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn("inline-block size-2 rounded-full", STATUS_DOT_CLASSES[status], className)}
      title={STATUS_LABELS[status]}
    />
  );
}

export default StatusBadge;
