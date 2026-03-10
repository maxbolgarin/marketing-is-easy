import { api } from "@/api/client";

export interface SettingItem {
  key: string;
  value: string;
  is_secret: boolean;
  label: string;
  group: string;
  source: "database" | "environment" | "default";
}

export interface SettingsGroup {
  group: string;
  label: string;
  settings: SettingItem[];
}

export interface HealthResponse {
  status: string;
  services: Record<string, string>;
}

export function getSettings(): Promise<SettingsGroup[]> {
  return api.get<SettingsGroup[]>("/api/settings");
}

export function updateSettings(settings: Record<string, string>): Promise<{ message: string }> {
  return api.put<{ message: string }>("/api/settings", { settings });
}

export function deleteSetting(key: string): Promise<{ message: string }> {
  return api.del<{ message: string }>(`/api/settings/${key}`);
}

export function getHealth(): Promise<HealthResponse> {
  return api.get<HealthResponse>("/api/health");
}
