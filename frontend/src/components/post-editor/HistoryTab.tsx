import { Clock, FileText, Cpu } from "lucide-react";

import StatusBadge from "@/components/shared/StatusBadge";
import { formatDateTime, formatRelative } from "@/lib/date";
import type { Post } from "@/lib/types";

interface HistoryTabProps {
  post: Post;
}

function InfoRow({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-sm">{value}</span>
    </div>
  );
}

export default function HistoryTab({ post }: HistoryTabProps) {
  const generationParams = post.generation_params ?? {};
  const hasParams = Object.keys(generationParams).length > 0;

  return (
    <div className="flex flex-col gap-5">
      <section className="flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <Clock className="size-3.5 text-muted-foreground" />
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
            Timeline
          </h3>
        </div>
        <div className="flex flex-col gap-3 rounded-xl border border-border bg-card px-4 py-3">
          <InfoRow
            label="Created"
            value={`${formatDateTime(post.created_at)} (${formatRelative(post.created_at)})`}
          />
          <InfoRow
            label="Last updated"
            value={`${formatDateTime(post.updated_at)} (${formatRelative(post.updated_at)})`}
          />
          {post.approved_at && (
            <InfoRow
              label="Approved"
              value={`${formatDateTime(post.approved_at)} by ${post.approved_by ?? "unknown"}`}
            />
          )}
        </div>
      </section>

      <section className="flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <FileText className="size-3.5 text-muted-foreground" />
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
            Post Info
          </h3>
        </div>
        <div className="flex flex-col gap-3 rounded-xl border border-border bg-card px-4 py-3">
          <InfoRow label="ID" value={<span className="font-mono text-xs">{post.id}</span>} />
          <InfoRow label="Status" value={<StatusBadge status={post.status} />} />
          <InfoRow label="Type" value={post.post_type} />
          <InfoRow label="Language" value={post.language ?? "—"} />
          <InfoRow label="Track" value={post.track} />
          {post.theme_id && (
            <InfoRow
              label="Theme ID"
              value={<span className="font-mono text-xs">{post.theme_id}</span>}
            />
          )}
          {post.scheduled_at && (
            <InfoRow
              label="Scheduled"
              value={formatDateTime(post.scheduled_at)}
            />
          )}
        </div>
      </section>

      {hasParams && (
        <section className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <Cpu className="size-3.5 text-muted-foreground" />
            <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
              Generation Params
            </h3>
          </div>
          <pre className="rounded-xl border border-border bg-muted/30 px-4 py-3 text-xs font-mono overflow-x-auto whitespace-pre-wrap break-all">
            {JSON.stringify(generationParams, null, 2)}
          </pre>
        </section>
      )}
    </div>
  );
}
