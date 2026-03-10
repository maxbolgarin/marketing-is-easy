import type { Asset } from "@/lib/types";
import { api, apiRequest, getToken } from "@/api/client";

/**
 * Returns all uploaded assets.
 */
export function getAssets(): Promise<Asset[]> {
  return api.get<Asset[]>("/assets");
}

/**
 * Uploads a file as a new asset.
 * Uses multipart/form-data — Content-Type is set automatically by the browser.
 */
export function uploadAsset(file: File): Promise<Asset> {
  const formData = new FormData();
  formData.append("file", file);

  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return apiRequest<Asset>("/assets", {
    method: "POST",
    headers,
    body: formData,
  });
}

/**
 * Deletes an asset by its storage path.
 */
export function deleteAsset(path: string): Promise<void> {
  const encodedPath = encodeURIComponent(path);
  return api.del<void>(`/assets/${encodedPath}`);
}
