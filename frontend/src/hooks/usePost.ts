import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  approvePost,
  createPost,
  deletePost,
  getPost,
  publishNow,
  rejectPost,
  updatePost,
} from "@/api/posts";
import type { ApprovePostData, CreatePostData, UpdatePostData } from "@/api/posts";

import { queryKeys } from "./queryKeys";

// ---------------------------------------------------------------------------
// usePost
// ---------------------------------------------------------------------------

export function usePost(id: string) {
  return useQuery({
    queryKey: queryKeys.posts.detail(id),
    queryFn: () => getPost(id),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "draft" || status === "generating" ? 3000 : false;
    },
    enabled: Boolean(id),
  });
}

// ---------------------------------------------------------------------------
// useCreatePost
// ---------------------------------------------------------------------------

export function useCreatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreatePostData) => createPost(data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
    },
  });
}

// ---------------------------------------------------------------------------
// useUpdatePost
// ---------------------------------------------------------------------------

interface UpdatePostVariables {
  id: string;
  data: UpdatePostData;
}

export function useUpdatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: UpdatePostVariables) => updatePost(id, data),
    onSuccess: (post) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.detail(post.id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
    },
  });
}

// ---------------------------------------------------------------------------
// useApprovePost
// ---------------------------------------------------------------------------

interface ApprovePostVariables {
  id: string;
  data?: ApprovePostData;
}

export function useApprovePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: ApprovePostVariables) => approvePost(id, data),
    onSuccess: (post) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.detail(post.id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats });
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.attention });
    },
  });
}

// ---------------------------------------------------------------------------
// useRejectPost
// ---------------------------------------------------------------------------

export function useRejectPost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => rejectPost(id),
    onSuccess: (post) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.detail(post.id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.attention });
    },
  });
}

// ---------------------------------------------------------------------------
// usePublishNow
// ---------------------------------------------------------------------------

export function usePublishNow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => publishNow(id),
    onSuccess: (post) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.detail(post.id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats });
    },
  });
}

// ---------------------------------------------------------------------------
// useDeletePost
// ---------------------------------------------------------------------------

export function useDeletePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deletePost(id),
    onSuccess: (_result, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.posts.detail(id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats });
    },
  });
}
