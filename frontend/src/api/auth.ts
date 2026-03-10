import type { User } from "@/lib/types";
import { api } from "@/api/client";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/**
 * Authenticate with username and password.
 */
export function login(username: string, password: string): Promise<LoginResponse> {
  return api.post<LoginResponse>("/auth/login", { username, password });
}

/**
 * Returns the currently authenticated user.
 */
export function getMe(): Promise<User> {
  return api.get<User>("/auth/me");
}
