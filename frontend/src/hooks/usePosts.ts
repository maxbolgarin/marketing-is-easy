import { useQuery } from "@tanstack/react-query";

import { getPosts } from "@/api/posts";
import type { PostsParams } from "@/api/posts";

import { queryKeys } from "./queryKeys";

// ---------------------------------------------------------------------------
// usePosts
// ---------------------------------------------------------------------------

export function usePosts(filters?: PostsParams) {
  return useQuery({
    queryKey: queryKeys.posts.list(filters),
    queryFn: () => getPosts(filters),
  });
}
