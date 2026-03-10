import type { User } from "@/lib/types";
import { api } from "@/api/client";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * Authenticate with username and password.
 * The backend expects form-encoded data for OAuth2 password flow.
 */
export function login(username: string, password: string): Promise<LoginResponse> {
  const body = new URLSearchParams({ username, password });
  return fetch(
    `${(import.meta.env.VITE_API_URL as string | undefined) ?? ""}/auth/token`,
    {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    },
  ).then(async (res) => {
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(
        typeof err === "object" && "detail" in err ? String(err.detail) : "Login failed",
      );
    }
    return res.json() as Promise<LoginResponse>;
  });
}

/**
 * Returns the currently authenticated user.
 */
export function getMe(): Promise<User> {
  return api.get<User>("/auth/me");
}
