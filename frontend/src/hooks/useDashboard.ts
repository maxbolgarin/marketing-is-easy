import { useQuery } from "@tanstack/react-query";

import { getAttention, getStats, getUpcoming } from "@/api/dashboard";

import { queryKeys } from "./queryKeys";

// ---------------------------------------------------------------------------
// useDashboardStats
// ---------------------------------------------------------------------------

export function useDashboardStats() {
  return useQuery({
    queryKey: queryKeys.dashboard.stats,
    queryFn: getStats,
    refetchInterval: 60_000,
  });
}

// ---------------------------------------------------------------------------
// useUpcoming
// ---------------------------------------------------------------------------

export function useUpcoming() {
  return useQuery({
    queryKey: queryKeys.dashboard.upcoming,
    queryFn: getUpcoming,
  });
}

// ---------------------------------------------------------------------------
// useAttention
// ---------------------------------------------------------------------------

export function useAttention() {
  return useQuery({
    queryKey: queryKeys.dashboard.attention,
    queryFn: getAttention,
  });
}
