import { Skeleton } from "@/components/ui/skeleton";
import StatusBadge from "@/components/shared/StatusBadge";
import PlatformIcon from "@/components/shared/PlatformIcon";
import { useEditorStore } from "@/stores/editor";
import { useUIStore } from "@/stores/ui";
import { usePosts } from "@/hooks/usePosts";
import { formatDateTime } from "@/lib/date";
import type { Post, Platform } from "@/lib/types";

function PostItem({ post }: { post: Post }) {
  const openEditor = useEditorStore((s) => s.openEditor);

  const preview = post.text_content
    ? post.text_content.slice(0, 60) + (post.text_content.length > 60 ? "…" : "")
    : post.text_prompt
      ? post.text_prompt.slice(0, 60) + "…"
      : "No content yet";

  const platforms = [...new Set(post.publications?.map((p) => p.platform) ?? [])];

  return (
    <button
      type="button"
      onClick={() => openEditor(post.id)}
      className="group relative w-full rounded-lg border border-border bg-card px-3 py-2.5 text-left transition-colors hover:bg-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      {post.theme?.color && (
        <span
          className="absolute inset-y-0 left-0 w-[3px] rounded-l-lg"
          style={{ backgroundColor: post.theme.color }}
        />
      )}
      <p className="text-sm truncate text-foreground">{preview}</p>
      <div className="flex items-center gap-2 mt-1.5 flex-wrap">
        <StatusBadge status={post.status} />
        {post.scheduled_at ? (
          <span className="text-[11px] text-muted-foreground">
            {formatDateTime(post.scheduled_at)}
          </span>
        ) : (
          <span className="text-[11px] text-muted-foreground italic">
            Unscheduled
          </span>
        )}
      </div>
      {platforms.length > 0 && (
        <div className="flex items-center gap-1 mt-1.5">
          {platforms.map((p) => (
            <PlatformIcon key={p} platform={p} className="size-3" />
          ))}
        </div>
      )}
    </button>
  );
}

export function PostsList() {
  const { filters } = useUIStore();

  const hasMultiFilter =
    filters.statuses.length > 1 ||
    filters.platforms.length > 1 ||
    filters.themes.length > 1;

  const postsQuery = usePosts({
    limit: hasMultiFilter ? 500 : 100,
    status: filters.statuses.length === 1 ? filters.statuses[0] as Post["status"] : undefined,
    platform: filters.platforms.length === 1 ? (filters.platforms[0] as Platform) : undefined,
    theme_id: filters.themes.length === 1 ? filters.themes[0] : undefined,
  });

  let posts = postsQuery.data?.items ?? [];
  const serverTotal = postsQuery.data?.total ?? 0;

  // Client-side filter for multi-value filters not supported by API
  if (filters.statuses.length > 1) {
    posts = posts.filter((p) => filters.statuses.includes(p.status));
  }
  if (filters.platforms.length > 1) {
    posts = posts.filter((p) =>
      p.publications?.some((pub) => filters.platforms.includes(pub.platform)),
    );
  }
  if (filters.themes.length > 1) {
    posts = posts.filter((p) => p.theme_id && filters.themes.includes(p.theme_id));
  }

  const truncated = hasMultiFilter && serverTotal > (postsQuery.data?.items.length ?? 0);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-1 pb-2">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
          All Posts
        </h3>
        <span className="text-xs text-muted-foreground">
          {postsQuery.data?.total ?? 0}
          {truncated && (
            <span className="text-yellow-400 ml-1" title="Some posts may not be shown due to filter limits">
              (partial)
            </span>
          )}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1.5 min-h-0">
        {postsQuery.isLoading && (
          <>
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full rounded-lg" />
            ))}
          </>
        )}

        {postsQuery.isError && (
          <p className="text-xs text-muted-foreground text-center py-6">
            Failed to load posts.
          </p>
        )}

        {!postsQuery.isLoading && posts.length === 0 && (
          <p className="text-xs text-muted-foreground text-center py-6">
            No posts yet.
          </p>
        )}

        {posts.map((post) => (
          <PostItem key={post.id} post={post} />
        ))}
      </div>
    </div>
  );
}
