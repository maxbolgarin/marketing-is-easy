import { useEffect, useRef, useState } from "react";
import { Copy, Save, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import StatusBadge from "@/components/shared/StatusBadge";
import { PLATFORM_LABELS } from "@/lib/constants";
import { cn } from "@/lib/utils";
import { usePost, useCreatePost } from "@/hooks/usePost";
import { usePostEditor } from "@/hooks/usePostEditor";
import type { Channel } from "@/lib/types";
import type { EditorTab } from "@/stores/editor";
import ChannelSelector from "./ChannelSelector";
import ContentTab from "./ContentTab";
import FormattingToolbar from "./FormattingToolbar";
import HistoryTab from "./HistoryTab";
import PlatformsTab from "./PlatformsTab";
import ScheduleTab from "./ScheduleTab";

const TABS: { value: EditorTab; label: string }[] = [
  { value: "content", label: "Content" },
  { value: "platforms", label: "Platforms" },
  { value: "schedule", label: "Schedule" },
  { value: "history", label: "History" },
];

function toLocalDatetimeString(isoString: string): string {
  const date = new Date(isoString);
  const offset = date.getTimezoneOffset() * 60000;
  const local = new Date(date.getTime() - offset);
  return local.toISOString().slice(0, 16);
}

function toISOString(localDatetime: string): string {
  return new Date(localDatetime).toISOString();
}

export default function PostEditorPanel() {
  const {
    isOpen,
    postId,
    scheduledDate,
    activeTab,
    openEditor,
    closeEditor,
    setActiveTab,
  } = usePostEditor();

  // Local state for new post form
  const [localContent, setLocalContent] = useState("");
  const [localChannel, setLocalChannel] = useState<Channel | null>(null);
  const [localSchedule, setLocalSchedule] = useState("");
  const [showDiscardConfirm, setShowDiscardConfirm] = useState(false);

  const newPostTextareaRef = useRef<HTMLTextAreaElement>(null);
  const createPost = useCreatePost();

  // Reset local state whenever the modal opens for a fresh new post
  useEffect(() => {
    if (isOpen && !postId) {
      setLocalContent("");
      setLocalChannel(null);
      setLocalSchedule(
        scheduledDate ? toLocalDatetimeString(scheduledDate) : "",
      );
      setShowDiscardConfirm(false);
    }
  }, [isOpen, postId, scheduledDate]);

  const { data: post, isLoading, isError } = usePost(postId ?? "");
  const isPolling = post?.status === "generating";

  const isDirty = !postId && Boolean(localContent || localChannel || localSchedule);

  function handleAttemptClose() {
    if (isDirty) {
      setShowDiscardConfirm(true);
    } else {
      closeEditor();
    }
  }

  function handleConfirmDiscard() {
    setShowDiscardConfirm(false);
    closeEditor();
  }

  function handleSaveNew() {
    if (!localChannel) return;
    createPost.mutate(
      {
        track: localChannel.track,
        text_content: localContent || undefined,
        scheduled_at: localSchedule ? toISOString(localSchedule) : undefined,
      },
      {
        onSuccess: (newPost) => {
          openEditor(newPost.id);
        },
      },
    );
  }

  function handleDuplicate() {
    if (!post) return;
    createPost.mutate(
      {
        track: post.track,
        text_content: post.text_content || undefined,
        theme_id: post.theme_id,
      },
      {
        onSuccess: (newPost) => {
          openEditor(newPost.id);
        },
      },
    );
  }

  const platformLabel = localChannel
    ? PLATFORM_LABELS[localChannel.platform] || localChannel.platform
    : "";

  return (
    <>
      <Dialog
        open={isOpen}
        onOpenChange={(open) => {
          if (!open) handleAttemptClose();
        }}
      >
        <DialogContent
          className="sm:max-w-4xl p-0 gap-0 flex flex-col max-h-[90vh] overflow-hidden"
          showCloseButton={false}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border px-5 py-4 shrink-0">
            <div className="flex items-center gap-2 min-w-0">
              {!postId ? (
                <h2 className="text-base font-semibold">New Post</h2>
              ) : isLoading ? (
                <Skeleton className="h-5 w-36" />
              ) : post ? (
                <>
                  <h2 className="text-base font-semibold truncate">
                    {post.text_content
                      ? post.text_content.slice(0, 40) +
                        (post.text_content.length > 40 ? "…" : "")
                      : "New Post"}
                  </h2>
                  <StatusBadge status={post.status} />
                  {isPolling && (
                    <span className="size-2 rounded-full bg-blue-400 animate-pulse" />
                  )}
                </>
              ) : (
                <h2 className="text-base font-semibold text-muted-foreground">
                  Post
                </h2>
              )}
            </div>
            <div className="flex items-center gap-1 shrink-0">
              {post && !isLoading && (
                <Button
                  variant="ghost"
                  size="icon-sm"
                  onClick={handleDuplicate}
                  disabled={createPost.isPending}
                  title="Duplicate post"
                >
                  <Copy className="size-4" />
                </Button>
              )}
              <Button
                variant="ghost"
                size="icon-sm"
                onClick={handleAttemptClose}
                aria-label="Close editor"
              >
                <X className="size-4" />
              </Button>
            </div>
          </div>

          {/* New post form */}
          {!postId && (
            <>
              <div className="flex-1 overflow-y-auto">
                <div className="flex flex-col gap-5 px-5 py-5">
                  {/* Channel selector */}
                  <section className="flex flex-col gap-2">
                    <div className="flex items-center gap-1">
                      <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                        Connection
                      </h3>
                      <span className="text-red-400 text-xs leading-none">
                        *
                      </span>
                    </div>
                    <ChannelSelector
                      value={localChannel?.id ?? null}
                      onChange={(_id, channel) => setLocalChannel(channel)}
                    />
                    {!localChannel && (
                      <p className="text-xs text-muted-foreground">
                        Select a social network — post format and text options
                        depend on the connection.
                      </p>
                    )}
                  </section>

                  <Separator />

                  {/* Text editor */}
                  <section className="flex flex-col gap-2">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                        Text Content
                      </h3>
                      <span className="text-xs text-muted-foreground">
                        {localContent.trim().split(/\s+/).filter(Boolean).length}{" "}
                        words
                      </span>
                    </div>
                    <FormattingToolbar
                      platform={localChannel?.platform}
                      textareaRef={newPostTextareaRef}
                      value={localContent}
                      onChange={(newValue) => setLocalContent(newValue)}
                    />
                    <Textarea
                      ref={newPostTextareaRef}
                      value={localContent}
                      onChange={(e) => setLocalContent(e.target.value)}
                      placeholder={
                        localChannel
                          ? `Write your ${platformLabel} post content...`
                          : "Select a connection first..."
                      }
                      disabled={!localChannel}
                      className={cn(
                        "min-h-[220px] resize-none text-sm",
                        localChannel && "rounded-t-none border-t-0",
                      )}
                    />
                  </section>

                  <Separator />

                  {/* Schedule */}
                  <section className="flex flex-col gap-2">
                    <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                      Schedule{" "}
                      <span className="normal-case font-normal">(optional)</span>
                    </h3>
                    <input
                      type="datetime-local"
                      value={localSchedule}
                      onChange={(e) => setLocalSchedule(e.target.value)}
                      className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm shadow-xs transition-colors focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50 [color-scheme:dark]"
                    />
                  </section>
                </div>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-end gap-2 border-t border-border px-5 py-3 shrink-0 bg-muted/30">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleAttemptClose}
                  disabled={createPost.isPending}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  disabled={!localChannel || createPost.isPending}
                  onClick={handleSaveNew}
                  className="gap-1.5"
                >
                  {createPost.isPending ? (
                    "Saving..."
                  ) : (
                    <>
                      <Save className="size-3.5" />
                      Save Post
                    </>
                  )}
                </Button>
              </div>
            </>
          )}

          {/* Existing post tabbed editor */}
          {postId && (
            <div className="flex-1 overflow-y-auto">
              {(isLoading || createPost.isPending) && <EditorSkeleton />}

              {isError && (
                <div className="flex flex-col items-center justify-center gap-3 py-20 text-muted-foreground px-6 text-center">
                  <p className="text-sm">
                    Could not load post. Please try again.
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={closeEditor}
                  >
                    Close
                  </Button>
                </div>
              )}

              {post && !isLoading && (
                <Tabs
                  value={activeTab}
                  onValueChange={(v) => setActiveTab(v as EditorTab)}
                  className="flex flex-col h-full"
                >
                  <TabsList
                    variant="line"
                    className="w-full justify-start rounded-none border-b border-border px-5 h-10 shrink-0"
                  >
                    {TABS.map((tab) => (
                      <TabsTrigger key={tab.value} value={tab.value}>
                        {tab.label}
                      </TabsTrigger>
                    ))}
                  </TabsList>

                  <div className="flex-1 overflow-y-auto px-5 py-4">
                    <TabsContent value="content">
                      <ContentTab post={post} />
                    </TabsContent>
                    <TabsContent value="platforms">
                      <PlatformsTab post={post} />
                    </TabsContent>
                    <TabsContent value="schedule">
                      <ScheduleTab post={post} />
                    </TabsContent>
                    <TabsContent value="history">
                      <HistoryTab post={post} />
                    </TabsContent>
                  </div>
                </Tabs>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Discard confirmation dialog */}
      <Dialog
        open={showDiscardConfirm}
        onOpenChange={(open) => {
          if (!open) setShowDiscardConfirm(false);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Discard changes?</DialogTitle>
            <DialogDescription>
              You have unsaved content. If you close, your changes will be lost.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowDiscardConfirm(false)}
            >
              Keep editing
            </Button>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleConfirmDiscard}
            >
              Discard & close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

function EditorSkeleton() {
  return (
    <div className="flex flex-col gap-4 p-5">
      <div className="flex gap-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-7 w-20" />
        ))}
      </div>
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-20 w-full" />
      <Skeleton className="h-4 w-24" />
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-4 w-16" />
      <Skeleton className="h-40 w-full rounded-xl" />
    </div>
  );
}
