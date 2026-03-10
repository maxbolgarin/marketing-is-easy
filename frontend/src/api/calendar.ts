import type { CalendarDay } from "@/lib/types";
import { api } from "@/api/client";

export interface RescheduleItem {
  post_id: string;
  new_scheduled_at: string;
}

export interface RescheduleResponse {
  message: string;
}

function buildQuery(params: Record<string, unknown>): string {
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      qs.set(key, String(value));
    }
  }
  const str = qs.toString();
  return str ? `?${str}` : "";
}

/**
 * Fetches calendar days with posts for the given date range.
 * Dates should be ISO strings, e.g. "2026-03-01".
 */
export function getCalendar(
  start: string,
  end: string,
  track?: string,
): Promise<CalendarDay[]> {
  const params: Record<string, unknown> = { start, end };
  if (track) {
    params.track = track;
  }
  return api.get<CalendarDay[]>(`/calendar${buildQuery(params)}`);
}

/**
 * Reschedules multiple posts in a single request.
 */
export function reschedule(items: RescheduleItem[]): Promise<RescheduleResponse> {
  return api.patch<RescheduleResponse>("/calendar/reschedule", { items });
}
