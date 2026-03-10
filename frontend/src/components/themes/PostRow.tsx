import { Eye, Pencil, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import PlatformIcon from "@/components/shared/PlatformIcon";
import StatusBadge from "@/components/shared/StatusBadge";
import { usePostEditor } from "@/hooks/usePostEditor";
import { formatDateTime } from "@/lib/date";
import type { Post } from "@/lib/types";

interface PostRowProps {
  post: Post;
  index?: number;
}

export default function PostRow({ post, index }: PostRowProps) {
  const { openEditor } = usePostEditor();

  const preview = post.text_content
    ? post.text_content.slice(0, 80) + (post.text_content.length > 80 ? "…" : "")
    : post.text_prompt
      ? post.text_prompt.slice(0, 80) + "…"
      : "No content yet";

  const platforms = post.publications?.map((p) => p.platform) ?? [];

  return (
    <div className="group flex items-center gap-4 rounded-xl border border-border bg-card px-4 py-3 transition-colors hover:bg-muted/20">
      {/* Index */}
      {index !== undefined && (
        <span className="text-xs font-mono text-muted-foreground w-5 shrink-0 text-right">
          {index + 1}
        </span>
      )}

      {/* Content preview */}
      <div className="flex-1 flex flex-col gap-1 min-w-0">
        <p className="text-sm truncate text-foreground">{preview}</p>
        <div className="flex items-center gap-2 flex-wrap">
          <StatusBadge status={post.status} />
          {post.scheduled_at && (
            <span className="text-xs text-muted-foreground">
              {formatDateTime(post.scheduled_at)}
            </span>
          )}
        </div>
      </div>

      {/* Platform icons */}
      {platforms.length > 0 && (
        <div className="flex items-center gap-1 shrink-0">
          {platforms.map((p) => (
            <PlatformIcon key={p} platform={p} className="size-3.5" />
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-1 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button
          variant="ghost"
          size="icon-sm"
          title="Preview"
          onClick={() => openEditor(post.id)}
        >
          <Eye className="size-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="icon-sm"
          title="Edit"
          onClick={() => openEditor(post.id)}
        >
          <Pencil className="size-3.5" />
        </Button>
        {(post.status === "draft" || post.status === "rejected") && (
          <Button
            variant="ghost"
            size="icon-sm"
            title="Generate"
            onClick={() => openEditor(post.id)}
          >
            <Sparkles className="size-3.5" />
          </Button>
        )}
      </div>
    </div>
  );
}
