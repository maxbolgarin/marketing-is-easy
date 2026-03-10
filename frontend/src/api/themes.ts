import type { Theme, Platform, ThemeStatus, PaginatedResponse } from "@/lib/types";
import { api } from "@/api/client";

export interface ThemesParams {
  status?: ThemeStatus;
  track?: string;
  limit?: number;
  offset?: number;
}

export interface CreateThemeData {
  name: string;
  description?: string;
  status?: ThemeStatus;
  target_platforms: Platform[];
  cadence_type: string;
  cadence_rule?: Record<string, unknown>;
  start_date?: string;
  end_date?: string;
  generation_context?: string;
  default_prompt_template?: string;
  color?: string;
  template_id?: string;
  track: string;
}

export interface UpdateThemeData {
  name?: string;
  description?: string;
  status?: ThemeStatus;
  target_platforms?: Platform[];
  cadence_type?: string;
  cadence_rule?: string;
  start_date?: string;
  end_date?: string;
  generation_context?: string;
  default_prompt_template?: string;
  color?: string;
}

export interface BatchGenerateData {
  count?: number;
  start_date?: string;
  end_date?: string;
  generation_params?: Record<string, unknown>;
}

export interface BatchGenerateResult {
  post_id: string;
  task_id: string;
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

export function getThemes(params?: ThemesParams): Promise<PaginatedResponse<Theme>> {
  return api.get<PaginatedResponse<Theme>>(`/themes${buildQuery(params as Record<string, unknown>)}`);
}

export function getTheme(id: string): Promise<Theme> {
  return api.get<Theme>(`/themes/${id}`);
}

export function createTheme(data: CreateThemeData): Promise<Theme> {
  return api.post<Theme>("/themes", data);
}

export function updateTheme(id: string, data: UpdateThemeData): Promise<Theme> {
  return api.patch<Theme>(`/themes/${id}`, data);
}

export function deleteTheme(id: string): Promise<void> {
  return api.del<void>(`/themes/${id}`);
}

export function batchGenerate(
  themeId: string,
  data: BatchGenerateData,
): Promise<BatchGenerateResult[]> {
  return api.post<BatchGenerateResult[]>(`/themes/${themeId}/batch-generate`, data);
}
