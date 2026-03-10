import type { PostStatus } from "@/lib/types";
import { STATUS_LABELS } from "@/lib/constants";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: PostStatus;
  className?: string;
}

const STATUS_VARIANT_CLASSES: Record<PostStatus, string> = {
  draft: "bg-zinc-800 text-zinc-400 border-zinc-700",
  generating: "bg-blue-950 text-blue-400 border-blue-800",
  review: "bg-yellow-950 text-yellow-400 border-yellow-800",
  approved: "bg-green-950 text-green-400 border-green-800",
  publishing: "bg-blue-950 text-blue-400 border-blue-800",
  published: "bg-emerald-950 text-emerald-400 border-emerald-800",
  failed: "bg-red-950 text-red-400 border-red-800",
  rejected: "bg-zinc-800 text-zinc-400 border-zinc-700",
};

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
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-1.5 py-0.5 text-xs font-medium",
        STATUS_VARIANT_CLASSES[status],
        className,
      )}
    >
      <span className={cn("size-1.5 rounded-full", STATUS_DOT_CLASSES[status])} />
      {STATUS_LABELS[status]}
    </span>
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
