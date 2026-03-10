const BASE_URL: string = (import.meta.env.VITE_API_URL as string | undefined) ?? "/api";

const TOKEN_KEY = "auth_token";

// ---------------------------------------------------------------------------
// Token helpers
// ---------------------------------------------------------------------------

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

// ---------------------------------------------------------------------------
// Core request helper
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  readonly status: number;
  readonly body?: unknown;
  constructor(status: number, message: string, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();

  const headers = new Headers(options.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (
    options.body !== undefined &&
    options.body !== null &&
    !(options.body instanceof FormData)
  ) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeToken();
    throw new ApiError(401, "Session expired — please log in again");
  }

  if (!response.ok) {
    let body: unknown;
    try {
      body = await response.json();
    } catch {
      body = await response.text();
    }
    const message =
      typeof body === "object" && body !== null && "detail" in body
        ? String((body as Record<string, unknown>).detail)
        : `HTTP ${response.status}`;
    throw new ApiError(response.status, message, body);
  }

  // 204 No Content
  if (response.status === 204) {
    return undefined as unknown as T;
  }

  return response.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Convenience methods
// ---------------------------------------------------------------------------

function get<T>(path: string, options?: RequestInit): Promise<T> {
  return apiRequest<T>(path, { ...options, method: "GET" });
}

function post<T>(path: string, body?: unknown, options?: RequestInit): Promise<T> {
  return apiRequest<T>(path, {
    ...options,
    method: "POST",
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

function patch<T>(path: string, body?: unknown, options?: RequestInit): Promise<T> {
  return apiRequest<T>(path, {
    ...options,
    method: "PATCH",
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

function put<T>(path: string, body?: unknown, options?: RequestInit): Promise<T> {
  return apiRequest<T>(path, {
    ...options,
    method: "PUT",
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

function del<T = void>(path: string, options?: RequestInit): Promise<T> {
  return apiRequest<T>(path, { ...options, method: "DELETE" });
}

export const api = { get, post, patch, put, del };
