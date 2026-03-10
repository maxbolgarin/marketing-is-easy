import type { Channel } from "@/lib/types";
import { api } from "@/api/client";

export interface UpdateChannelData {
  account_name?: string;
  config?: Record<string, unknown>;
  is_active?: boolean;
}

export interface TestChannelResponse {
  message: string;
}

/**
 * Returns all configured publishing channels.
 */
export function getChannels(): Promise<Channel[]> {
  return api.get<Channel[]>("/channels");
}

/**
 * Updates configuration or active state for a channel.
 */
export function updateChannel(id: string, data: UpdateChannelData): Promise<Channel> {
  return api.patch<Channel>(`/channels/${id}`, data);
}

/**
 * Sends a test message / ping through the channel to verify connectivity.
 */
export function testChannel(id: string): Promise<TestChannelResponse> {
  return api.post<TestChannelResponse>(`/channels/${id}/test`);
}
