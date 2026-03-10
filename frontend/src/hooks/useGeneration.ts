import { useMutation, useQueryClient } from "@tanstack/react-query";

import { generateImage, generateText, generateVideo } from "@/api/posts";
import type { GenerateImageData, GenerateTextData } from "@/api/posts";

import { queryKeys } from "./queryKeys";

// ---------------------------------------------------------------------------
// useGenerateText
// ---------------------------------------------------------------------------

interface GenerateTextVariables {
  id: string;
  data?: GenerateTextData;
}

export function useGenerateText() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: GenerateTextVariables) => generateText(id, data),
    onSuccess: (post) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.detail(post.id) });
    },
  });
}

// ---------------------------------------------------------------------------
// useGenerateImage
// ---------------------------------------------------------------------------

interface GenerateImageVariables {
  id: string;
  data?: GenerateImageData;
}

export function useGenerateImage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: GenerateImageVariables) => generateImage(id, data),
    onSuccess: (post) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.detail(post.id) });
    },
  });
}

// ---------------------------------------------------------------------------
// useGenerateVideo
// ---------------------------------------------------------------------------

export function useGenerateVideo() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => generateVideo(id),
    onSuccess: (post) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.detail(post.id) });
    },
  });
}
