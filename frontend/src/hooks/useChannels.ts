import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getChannels, updateChannel, testChannel } from "@/api/channels";
import type { UpdateChannelData } from "@/api/channels";
import { queryKeys } from "./queryKeys";

// ---------------------------------------------------------------------------
// useChannels
// ---------------------------------------------------------------------------

export function useChannels() {
  return useQuery({
    queryKey: queryKeys.channels,
    queryFn: getChannels,
  });
}

// ---------------------------------------------------------------------------
// useUpdateChannel
// ---------------------------------------------------------------------------

interface UpdateChannelVariables {
  id: string;
  data: UpdateChannelData;
}

export function useUpdateChannel() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: UpdateChannelVariables) =>
      updateChannel(id, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.channels });
    },
  });
}

// ---------------------------------------------------------------------------
// useTestChannel
// ---------------------------------------------------------------------------

export function useTestChannel() {
  return useMutation({
    mutationFn: (id: string) => testChannel(id),
  });
}
