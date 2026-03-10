import { useParams } from "react-router";
import { AlertCircle } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";
import PostRow from "@/components/themes/PostRow";
import ThemeHeader from "@/components/themes/ThemeHeader";
import PostEditorPanel from "@/components/post-editor/PostEditorPanel";
import { usePosts } from "@/hooks/usePosts";
import { useTheme } from "@/hooks/useTheme";

export default function ThemeDetail() {
  const { id } = useParams<{ id: string }>();
  const themeQuery = useTheme(id ?? "");
  const postsQuery = usePosts({ theme_id: id });

  const posts = postsQuery.data?.items ?? [];

  if (themeQuery.isLoading) {
    return (
      <div className="flex flex-col gap-6 p-6">
        <div className="flex flex-col gap-3 pb-4 border-b border-border">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
          <Skeleton className="h-4 w-48" />
        </div>
        <div className="flex flex-col gap-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (themeQuery.isError || !themeQuery.data) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-20 text-muted-foreground p-6">
        <AlertCircle className="size-8" />
        <p className="text-sm">Theme not found.</p>
      </div>
    );
  }

  return (
    <>
      <div className="flex flex-col gap-6 p-6">
        <ThemeHeader theme={themeQuery.data} />

        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
              Posts
            </h2>
            {postsQuery.isLoading && (
              <span className="text-xs text-muted-foreground animate-pulse">
                Loading...
              </span>
            )}
          </div>

          {postsQuery.isError && (
            <p className="text-sm text-muted-foreground py-4">
              Failed to load posts.
            </p>
          )}

          {!postsQuery.isLoading && posts.length === 0 && (
            <p className="text-sm text-muted-foreground py-8 text-center">
              No posts in this theme yet.
            </p>
          )}

          {posts.map((post, i) => (
            <PostRow key={post.id} post={post} index={i} />
          ))}
        </div>
      </div>

      <PostEditorPanel />
    </>
  );
}
