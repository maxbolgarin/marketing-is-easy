import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getCalendar, reschedule } from "@/api/calendar";
import type { RescheduleItem } from "@/api/calendar";

import { queryKeys } from "./queryKeys";

// ---------------------------------------------------------------------------
// useCalendar
// ---------------------------------------------------------------------------

export function useCalendar(start: string, end: string, track?: string) {
  return useQuery({
    queryKey: [...queryKeys.calendar(start, end), track] as const,
    queryFn: () => getCalendar(start, end, track),
    enabled: Boolean(start) && Boolean(end),
  });
}

// ---------------------------------------------------------------------------
// useReschedule
// ---------------------------------------------------------------------------

export function useReschedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (items: RescheduleItem[]) => reschedule(items),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["calendar"] });
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
    },
  });
}
