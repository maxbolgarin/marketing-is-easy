import type { DashboardStats, Post } from "@/lib/types";
import { api } from "@/api/client";

export interface UpcomingResponse {
  posts: Post[];
}

export interface AttentionResponse {
  pending_review: Post[];
  failed: Post[];
}

/**
 * Returns high-level dashboard statistics.
 */
export function getStats(): Promise<DashboardStats> {
  return api.get<DashboardStats>("/dashboard/stats");
}

/**
 * Returns posts scheduled to be published in the near future.
 */
export function getUpcoming(): Promise<UpcomingResponse> {
  return api.get<UpcomingResponse>("/dashboard/upcoming");
}

/**
 * Returns posts that require human attention (pending review or failed).
 */
export function getAttention(): Promise<AttentionResponse> {
  return api.get<AttentionResponse>("/dashboard/attention");
}
