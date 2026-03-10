import { Bold, Italic, Strikethrough, Code, Link, Hash, AtSign } from "lucide-react";

import { Button } from "@/components/ui/button";
import { PLATFORM_CHAR_LIMITS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type { Platform } from "@/lib/types";

interface FormattingToolbarProps {
  platform: Platform | undefined;
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
  value: string;
  onChange: (newValue: string) => void;
}

export function wrapSelection(
  ref: React.RefObject<HTMLTextAreaElement | null>,
  prefix: string,
  suffix: string,
  onChange: (newValue: string) => void,
) {
  const el = ref.current;
  if (!el) return;
  const start = el.selectionStart;
  const end = el.selectionEnd;
  const value = el.value;
  const selected = value.slice(start, end) || "text";
  const newValue =
    value.slice(0, start) + prefix + selected + suffix + value.slice(end);
  onChange(newValue);
  requestAnimationFrame(() => {
    el.setSelectionRange(
      start + prefix.length,
      start + prefix.length + selected.length,
    );
    el.focus();
  });
}

export function insertAtCursor(
  ref: React.RefObject<HTMLTextAreaElement | null>,
  text: string,
  onChange: (newValue: string) => void,
) {
  const el = ref.current;
  if (!el) return;
  const start = el.selectionStart;
  const value = el.value;
  const newValue = value.slice(0, start) + text + value.slice(start);
  onChange(newValue);
  requestAnimationFrame(() => {
    el.setSelectionRange(start + text.length, start + text.length);
    el.focus();
  });
}

function ToolbarButton({
  onClick,
  children,
  title,
}: {
  onClick: () => void;
  children: React.ReactNode;
  title: string;
}) {
  return (
    <Button
      type="button"
      variant="ghost"
      size="icon-sm"
      onClick={onClick}
      title={title}
      className="size-6 rounded-sm text-muted-foreground hover:text-foreground"
    >
      {children}
    </Button>
  );
}

export default function FormattingToolbar({
  platform,
  textareaRef,
  value,
  onChange,
}: FormattingToolbarProps) {
  if (!platform) return null;

  const charLimit = PLATFORM_CHAR_LIMITS[platform];
  const charCount = value.length;
  const isOverLimit = charCount > charLimit;

  const wrap = (prefix: string, suffix: string) =>
    wrapSelection(textareaRef, prefix, suffix, onChange);
  const insert = (text: string) => insertAtCursor(textareaRef, text, onChange);

  const hasTelegramFormatting = platform === "telegram";
  const hasInstagramHelpers =
    platform === "instagram_post" || platform === "instagram_reel";

  return (
    <div className="flex items-center justify-between gap-1 px-2 py-1 rounded-t-lg border border-b-0 border-border bg-muted/40">
      <div className="flex items-center gap-0.5">
        {hasTelegramFormatting && (
          <>
            <ToolbarButton title="Bold (*text*)" onClick={() => wrap("*", "*")}>
              <Bold className="size-3.5" />
            </ToolbarButton>
            <ToolbarButton
              title="Italic (_text_)"
              onClick={() => wrap("_", "_")}
            >
              <Italic className="size-3.5" />
            </ToolbarButton>
            <ToolbarButton
              title="Strikethrough (~text~)"
              onClick={() => wrap("~", "~")}
            >
              <Strikethrough className="size-3.5" />
            </ToolbarButton>
            <ToolbarButton
              title="Code (`text`)"
              onClick={() => wrap("`", "`")}
            >
              <Code className="size-3.5" />
            </ToolbarButton>
            <ToolbarButton
              title="Spoiler (||text||)"
              onClick={() => wrap("||", "||")}
            >
              <span className="text-[11px] font-mono leading-none">||</span>
            </ToolbarButton>
            <ToolbarButton
              title="Link ([text](url))"
              onClick={() => wrap("[", "](url)")}
            >
              <Link className="size-3.5" />
            </ToolbarButton>
          </>
        )}
        {hasInstagramHelpers && (
          <>
            <ToolbarButton
              title="Insert hashtag"
              onClick={() => insert("#")}
            >
              <Hash className="size-3.5" />
            </ToolbarButton>
            <ToolbarButton
              title="Insert mention"
              onClick={() => insert("@")}
            >
              <AtSign className="size-3.5" />
            </ToolbarButton>
          </>
        )}
      </div>
      <span
        className={cn(
          "text-xs tabular-nums pr-0.5 shrink-0",
          isOverLimit ? "text-red-400 font-medium" : "text-muted-foreground",
        )}
      >
        {charCount}/{charLimit}
      </span>
    </div>
  );
}
