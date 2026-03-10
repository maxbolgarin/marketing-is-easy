import { useState } from "react";
import { Edit2, CheckCircle2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import PlatformIcon from "@/components/shared/PlatformIcon";
import StatusBadge from "@/components/shared/StatusBadge";
import { PLATFORM_CHAR_LIMITS, PLATFORM_LABELS } from "@/lib/constants";
import type { Publication } from "@/lib/types";
import { cn } from "@/lib/utils";

interface PlatformVariantCardProps {
  publication: Publication;
  onUpdate: (data: { platform_text?: string; is_enabled?: boolean }) => void;
}

export default function PlatformVariantCard({
  publication,
  onUpdate,
}: PlatformVariantCardProps) {
  const [enabled, setEnabled] = useState(publication.status !== "rejected");
  const [editing, setEditing] = useState(false);
  const [editedText, setEditedText] = useState(publication.platform_text ?? "");

  const charLimit = PLATFORM_CHAR_LIMITS[publication.platform] ?? 0;
  const charCount = (publication.platform_text ?? "").length;
  const overLimit = charLimit > 0 && charCount > charLimit;

  function handleToggle() {
    const next = !enabled;
    setEnabled(next);
    onUpdate({ is_enabled: next });
  }

  function handleSave() {
    onUpdate({ platform_text: editedText });
    setEditing(false);
  }

  return (
    <div
      className={cn(
        "flex flex-col gap-3 rounded-xl border border-border bg-card p-4 transition-opacity",
        !enabled && "opacity-50",
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <PlatformIcon platform={publication.platform} />
          <span className="text-sm font-medium">
            {PLATFORM_LABELS[publication.platform] ?? publication.platform}
          </span>
          <StatusBadge status={publication.status} />
        </div>
        <button
          role="switch"
          aria-checked={enabled}
          onClick={handleToggle}
          className={cn(
            "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200",
            enabled ? "bg-primary" : "bg-muted",
          )}
        >
          <span
            className={cn(
              "pointer-events-none inline-block size-4 rounded-full bg-white shadow-lg transition-transform duration-200",
              enabled ? "translate-x-4" : "translate-x-0",
            )}
          />
          <span className="sr-only">
            {enabled ? "Disable" : "Enable"} {PLATFORM_LABELS[publication.platform]}
          </span>
        </button>
      </div>

      {editing ? (
        <div className="flex flex-col gap-2">
          <Textarea
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            className={cn(
              "min-h-[100px] resize-none text-sm",
              overLimit && "border-red-500 focus-visible:border-red-500",
            )}
            autoFocus
          />
          <div className="flex items-center justify-between">
            <span
              className={cn(
                "text-xs",
                overLimit ? "text-red-400" : "text-muted-foreground",
              )}
            >
              {charCount}
              {charLimit > 0 && ` / ${charLimit}`}
            </span>
            <div className="flex gap-1.5">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setEditing(false)}
              >
                Cancel
              </Button>
              <Button size="sm" onClick={handleSave} className="gap-1">
                <CheckCircle2 className="size-3.5" />
                Save
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          <p className="text-sm text-muted-foreground leading-relaxed line-clamp-3">
            {publication.platform_text ?? (
              <span className="italic opacity-60">Not adapted yet</span>
            )}
          </p>
          <div className="flex items-center justify-between">
            <span
              className={cn(
                "text-xs",
                overLimit ? "text-red-400" : "text-muted-foreground",
              )}
            >
              {charCount}
              {charLimit > 0 && ` / ${charLimit}`}
            </span>
            <Button
              variant="ghost"
              size="xs"
              onClick={() => {
                setEditedText(publication.platform_text ?? "");
                setEditing(true);
              }}
              className="gap-1"
            >
              <Edit2 className="size-3" />
              Edit
            </Button>
          </div>
        </div>
      )}

      {publication.error_message && (
        <p className="text-xs text-red-400 rounded-md bg-red-950/40 px-2.5 py-1.5">
          {publication.error_message}
        </p>
      )}
    </div>
  );
}
