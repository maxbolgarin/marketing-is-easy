import { useParams } from "react-router";
import { AlertCircle, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import PostRow from "@/components/themes/PostRow";
import PlatformIcon from "@/components/shared/PlatformIcon";
import { usePosts } from "@/hooks/usePosts";
import { useEditorStore } from "@/stores/editor";
import { PLATFORM_LABELS } from "@/lib/constants";
import type { Platform } from "@/lib/types";

export default function Channel() {
  const { platform } = useParams<{ platform: string }>();
  const openEditor = useEditorStore((s) => s.openEditor);

  const postsQuery = usePosts({
    platform: platform as Platform,
    limit: 50,
  });

  const posts = postsQuery.data?.items ?? [];
  const platformLabel =
    PLATFORM_LABELS[platform as Platform] ?? platform ?? "Channel";

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between pb-4 border-b border-border">
        <div className="flex items-center gap-3">
          {platform && <PlatformIcon platform={platform} className="size-6" />}
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{platformLabel}</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              Posts targeted to this channel.
            </p>
          </div>
        </div>
        <Button size="sm" onClick={() => openEditor("")}>
          <Plus className="size-4" />
          New Post
        </Button>
      </div>

      {postsQuery.isLoading && (
        <div className="flex flex-col gap-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-xl" />
          ))}
        </div>
      )}

      {postsQuery.isError && (
        <div className="flex flex-col items-center justify-center gap-3 py-20 text-muted-foreground">
          <AlertCircle className="size-8" />
          <p className="text-sm">Failed to load posts.</p>
        </div>
      )}

      {!postsQuery.isLoading && !postsQuery.isError && posts.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-3 py-20 text-muted-foreground">
          <p className="text-sm">No posts for this channel yet.</p>
          <p className="text-xs max-w-sm text-center">
            Create a post and add a {platformLabel} variant in the Platforms tab to see it here.
          </p>
          <Button size="sm" variant="outline" onClick={() => openEditor("")}>
            <Plus className="size-3.5" />
            Create Post
          </Button>
        </div>
      )}

      {posts.length > 0 && (
        <div className="flex flex-col gap-2">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
            Posts ({postsQuery.data?.total ?? posts.length})
          </h2>
          {posts.map((post, i) => (
            <PostRow key={post.id} post={post} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
