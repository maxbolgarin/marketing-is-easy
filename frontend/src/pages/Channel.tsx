import { useParams } from "react-router";
import { AlertCircle } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import PostRow from "@/components/themes/PostRow";
import PlatformIcon from "@/components/shared/PlatformIcon";
import PostEditorPanel from "@/components/post-editor/PostEditorPanel";
import { usePosts } from "@/hooks/usePosts";
import { PLATFORM_LABELS } from "@/lib/constants";
import type { Platform } from "@/lib/types";

export default function Channel() {
  const { platform } = useParams<{ platform: string }>();

  const postsQuery = usePosts({
    platform: platform as Platform,
    limit: 50,
  });

  const posts = postsQuery.data?.items ?? [];
  const platformLabel =
    PLATFORM_LABELS[platform as Platform] ?? platform ?? "Channel";

  return (
    <>
      <div className="flex flex-col gap-6 p-6">
        <div className="flex items-center gap-3 pb-4 border-b border-border">
          {platform && <PlatformIcon platform={platform} className="size-6" />}
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{platformLabel}</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              Posts targeted to this channel.
            </p>
          </div>
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
          <div className="flex flex-col items-center justify-center gap-2 py-20 text-muted-foreground">
            <p className="text-sm">No posts for this channel yet.</p>
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

      <PostEditorPanel />
    </>
  );
}
