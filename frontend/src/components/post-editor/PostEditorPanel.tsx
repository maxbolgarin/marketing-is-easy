import { useEffect, useRef } from "react";
import { X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import StatusBadge from "@/components/shared/StatusBadge";
import { DEFAULT_TRACK } from "@/lib/constants";
import { usePost, useCreatePost } from "@/hooks/usePost";
import { usePostEditor } from "@/hooks/usePostEditor";
import type { EditorTab } from "@/stores/editor";
import ContentTab from "./ContentTab";
import HistoryTab from "./HistoryTab";
import PlatformsTab from "./PlatformsTab";
import ScheduleTab from "./ScheduleTab";

const TABS: { value: EditorTab; label: string }[] = [
  { value: "content", label: "Content" },
  { value: "platforms", label: "Platforms" },
  { value: "schedule", label: "Schedule" },
  { value: "history", label: "History" },
];

export default function PostEditorPanel() {
  const { isOpen, postId, scheduledDate, activeTab, openEditor, closeEditor, setActiveTab } =
    usePostEditor();

  const createPost = useCreatePost();
  const creatingRef = useRef(false);

  // Auto-create a draft post when editor opens with no postId
  useEffect(() => {
    if (isOpen && !postId && !creatingRef.current) {
      creatingRef.current = true;
      createPost.mutate(
        {
          track: DEFAULT_TRACK,
          scheduled_at: scheduledDate ?? undefined,
        },
        {
          onSuccess: (post) => {
            openEditor(post.id);
            creatingRef.current = false;
          },
          onError: () => {
            creatingRef.current = false;
            closeEditor();
          },
        },
      );
    }
  }, [isOpen, postId]);

  const { data: post, isLoading, isError } = usePost(postId ?? "");

  const isPolling = post?.status === "generating";

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && closeEditor()}>
      <SheetContent
        side="right"
        showCloseButton={false}
        className="w-full sm:max-w-xl flex flex-col gap-0 p-0"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-5 py-4 shrink-0">
          <div className="flex items-center gap-2 min-w-0">
            {isLoading ? (
              <Skeleton className="h-5 w-36" />
            ) : post ? (
              <>
                <h2 className="text-base font-semibold truncate">
                  {post.text_content
                    ? post.text_content.slice(0, 40) + (post.text_content.length > 40 ? "…" : "")
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
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={closeEditor}
            aria-label="Close editor"
          >
            <X />
          </Button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto">
          {(isLoading || createPost.isPending) && <EditorSkeleton />}

          {isError && (
            <div className="flex flex-col items-center justify-center gap-3 py-20 text-muted-foreground px-6 text-center">
              <p className="text-sm">Could not load post. Please try again.</p>
              <Button variant="outline" size="sm" onClick={closeEditor}>
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
      </SheetContent>
    </Sheet>
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
