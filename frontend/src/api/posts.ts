import type { Post, Publication, PaginatedResponse, PostStatus, Platform } from "@/lib/types";
import { api } from "@/api/client";

export interface PostsParams {
  status?: PostStatus;
  platform?: Platform;
  track?: string;
  theme_id?: string;
  limit?: number;
  offset?: number;
  scheduled_after?: string;
  scheduled_before?: string;
}

export interface CreatePostData {
  track: string;
  language?: string;
  post_type?: string;
  text_content?: string;
  text_prompt?: string;
  media_type?: string;
  media_urls?: string[];
  scheduled_at?: string;
  theme_id?: string;
  generation_params?: Record<string, unknown>;
}

export interface UpdatePostData {
  text_content?: string;
  text_prompt?: string;
  media_type?: string;
  media_urls?: string[];
  scheduled_at?: string | null;
  status?: PostStatus;
  generation_params?: Record<string, unknown>;
}

export interface GenerateTextData {
  prompt?: string;
  model?: string;
  generation_params?: Record<string, unknown>;
}

export interface GenerateImageData {
  prompt?: string;
  generation_params?: Record<string, unknown>;
}

export interface ApprovePostData {
  platform_overrides?: Partial<Record<Platform, string>>;
}

export interface CreateVariantData {
  platform: Platform;
  platform_text?: string;
  platform_media_url?: string;
}

export interface UpdateVariantData {
  platform_text?: string;
  platform_media_url?: string;
  status?: PostStatus;
}

function buildQuery(params?: Record<string, unknown>): string {
  if (!params) return "";
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      qs.set(key, String(value));
    }
  }
  const str = qs.toString();
  return str ? `?${str}` : "";
}

export function getPosts(params?: PostsParams): Promise<PaginatedResponse<Post>> {
  return api.get<PaginatedResponse<Post>>(`/posts${buildQuery(params as Record<string, unknown>)}`);
}

export function getPost(id: string): Promise<Post> {
  return api.get<Post>(`/posts/${id}`);
}

export function createPost(data: CreatePostData): Promise<Post> {
  return api.post<Post>("/posts", data);
}

export function updatePost(id: string, data: UpdatePostData): Promise<Post> {
  return api.patch<Post>(`/posts/${id}`, data);
}

export function deletePost(id: string): Promise<void> {
  return api.del<void>(`/posts/${id}`);
}

export function generateText(id: string, data?: GenerateTextData): Promise<Post> {
  return api.post<Post>(`/posts/${id}/generate-text`, data ?? {});
}

export function generateImage(id: string, data?: GenerateImageData): Promise<Post> {
  return api.post<Post>(`/posts/${id}/generate-image`, data ?? {});
}

export function generateVideo(id: string): Promise<Post> {
  return api.post<Post>(`/posts/${id}/generate-video`);
}

export function approvePost(id: string, data?: ApprovePostData): Promise<Post> {
  return api.post<Post>(`/posts/${id}/approve`, data ?? {});
}

export function rejectPost(id: string): Promise<Post> {
  return api.post<Post>(`/posts/${id}/reject`);
}

export function publishNow(id: string): Promise<Post> {
  return api.post<Post>(`/posts/${id}/publish-now`);
}

export function getVariants(id: string): Promise<Publication[]> {
  return api.get<Publication[]>(`/posts/${id}/variants`);
}

export function createVariant(id: string, data: CreateVariantData): Promise<Publication> {
  return api.post<Publication>(`/posts/${id}/variants`, data);
}

export function updateVariant(
  postId: string,
  variantId: string,
  data: UpdateVariantData,
): Promise<Publication> {
  return api.patch<Publication>(`/posts/${postId}/variants/${variantId}`, data);
}
