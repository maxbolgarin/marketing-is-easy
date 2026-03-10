import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  batchGenerate,
  createTheme,
  deleteTheme,
  getTheme,
  getThemes,
  updateTheme,
} from "@/api/themes";
import type {
  BatchGenerateData,
  CreateThemeData,
  ThemesParams,
  UpdateThemeData,
} from "@/api/themes";

import { queryKeys } from "./queryKeys";

// ---------------------------------------------------------------------------
// useTheme
// ---------------------------------------------------------------------------

export function useTheme(id: string) {
  return useQuery({
    queryKey: queryKeys.themes.detail(id),
    queryFn: () => getTheme(id),
    enabled: Boolean(id),
  });
}

// ---------------------------------------------------------------------------
// useThemes
// ---------------------------------------------------------------------------

export function useThemes(filters?: ThemesParams) {
  return useQuery({
    queryKey: queryKeys.themes.list(filters),
    queryFn: () => getThemes(filters),
  });
}

// ---------------------------------------------------------------------------
// useCreateTheme
// ---------------------------------------------------------------------------

export function useCreateTheme() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateThemeData) => createTheme(data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.themes.all });
    },
  });
}

// ---------------------------------------------------------------------------
// useUpdateTheme
// ---------------------------------------------------------------------------

interface UpdateThemeVariables {
  id: string;
  data: UpdateThemeData;
}

export function useUpdateTheme() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: UpdateThemeVariables) => updateTheme(id, data),
    onSuccess: (theme) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.themes.detail(theme.id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.themes.all });
    },
  });
}

// ---------------------------------------------------------------------------
// useDeleteTheme
// ---------------------------------------------------------------------------

export function useDeleteTheme() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteTheme(id),
    onSuccess: (_result, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.themes.detail(id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.themes.all });
    },
  });
}

// ---------------------------------------------------------------------------
// useBatchGenerate
// ---------------------------------------------------------------------------

interface BatchGenerateVariables {
  themeId: string;
  data: BatchGenerateData;
}

export function useBatchGenerate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ themeId, data }: BatchGenerateVariables) =>
      batchGenerate(themeId, data),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.posts.all });
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.stats });
    },
  });
}
