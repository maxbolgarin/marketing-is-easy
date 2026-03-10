import { useState, useEffect, useRef } from "react";
import { Edit2, CheckCircle2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useGenerateText } from "@/hooks/useGeneration";
import { useUpdatePost } from "@/hooks/usePost";
import type { Post } from "@/lib/types";
import { cn } from "@/lib/utils";
import GenerateButton from "./GenerateButton";

type TextMode = "static" | "generated";

interface TextSectionProps {
  post: Post;
  onUpdate: (data: Partial<Pick<Post, "text_content" | "text_prompt">>) => void;
}

export default function TextSection({ post, onUpdate }: TextSectionProps) {
  const [mode, setMode] = useState<TextMode>(
    post.text_prompt ? "generated" : "static",
  );
  const [editingGenerated, setEditingGenerated] = useState(false);
  const [editedText, setEditedText] = useState(post.text_content ?? "");

  // Local state for inputs — prevents refetch from overwriting while typing
  const [localContent, setLocalContent] = useState(post.text_content ?? "");
  const [localPrompt, setLocalPrompt] = useState(post.text_prompt ?? "");
  const contentFocused = useRef(false);
  const promptFocused = useRef(false);

  // Sync server → local only when user is NOT editing
  useEffect(() => {
    if (!contentFocused.current) {
      setLocalContent(post.text_content ?? "");
    }
  }, [post.text_content]);

  useEffect(() => {
    if (!promptFocused.current) {
      setLocalPrompt(post.text_prompt ?? "");
    }
  }, [post.text_prompt]);

  const generateText = useGenerateText();
  const updatePost = useUpdatePost();

  const wordCount = localContent.trim().split(/\s+/).filter(Boolean).length;
  const isGenerating =
    generateText.isPending || post.status === "generating";

  function handleGenerate() {
    generateText.mutate({
      id: post.id,
      data: { prompt: localPrompt },
    });
  }

  function handleSaveEdit() {
    updatePost.mutate({ id: post.id, data: { text_content: editedText } });
    onUpdate({ text_content: editedText });
    setEditingGenerated(false);
  }

  function handleContentBlur() {
    contentFocused.current = false;
    if (localContent !== (post.text_content ?? "")) {
      onUpdate({ text_content: localContent });
    }
  }

  function handlePromptBlur() {
    promptFocused.current = false;
    if (localPrompt !== (post.text_prompt ?? "")) {
      onUpdate({ text_prompt: localPrompt });
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-1 rounded-lg bg-muted p-0.5 w-fit">
        {(["static", "generated"] as TextMode[]).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={cn(
              "rounded-md px-3 py-1 text-xs font-medium capitalize transition-colors",
              mode === m
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {m}
          </button>
        ))}
      </div>

      {mode === "generated" ? (
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Prompt
            </label>
            <Textarea
              value={localPrompt}
              onChange={(e) => setLocalPrompt(e.target.value)}
              onFocus={() => { promptFocused.current = true; }}
              onBlur={handlePromptBlur}
              placeholder="Describe what you want to generate..."
              className="min-h-[80px] resize-none text-sm"
            />
          </div>

          <div className="flex items-center justify-between">
            <GenerateButton
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
            />
            {post.status === "generating" && (
              <span className="text-xs text-blue-400 animate-pulse">
                AI is writing...
              </span>
            )}
          </div>

          {post.text_content && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  Generated Text
                </label>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">
                    {wordCount} words
                  </span>
                  {!editingGenerated && (
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => {
                        setEditedText(post.text_content ?? "");
                        setEditingGenerated(true);
                      }}
                    >
                      <Edit2 className="size-3.5" />
                    </Button>
                  )}
                  {editingGenerated && (
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={handleSaveEdit}
                    >
                      <CheckCircle2 className="size-3.5 text-green-400" />
                    </Button>
                  )}
                </div>
              </div>

              {editingGenerated ? (
                <Textarea
                  value={editedText}
                  onChange={(e) => setEditedText(e.target.value)}
                  className="min-h-[160px] resize-none text-sm"
                  autoFocus
                />
              ) : (
                <div className="rounded-lg border border-border bg-muted/30 px-3 py-2.5 text-sm whitespace-pre-wrap leading-relaxed">
                  {post.text_content}
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center justify-between">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Text Content
            </label>
            <span className="text-xs text-muted-foreground">
              {wordCount} words
            </span>
          </div>
          <Textarea
            value={localContent}
            onChange={(e) => setLocalContent(e.target.value)}
            onFocus={() => { contentFocused.current = true; }}
            onBlur={handleContentBlur}
            placeholder="Write your post content..."
            className="min-h-[160px] resize-none text-sm"
          />
        </div>
      )}
    </div>
  );
}
