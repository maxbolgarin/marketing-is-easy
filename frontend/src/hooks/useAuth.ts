import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";

import { getMe, login } from "@/api/auth";
import { getToken, removeToken, setToken } from "@/api/client";

// ---------------------------------------------------------------------------
// useLogin
// ---------------------------------------------------------------------------

interface LoginVariables {
  username: string;
  password: string;
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ username, password }: LoginVariables) =>
      login(username, password),
    onSuccess: (data) => {
      setToken(data.access_token);
      void queryClient.invalidateQueries({ queryKey: ["me"] });
    },
  });
}

// ---------------------------------------------------------------------------
// useMe
// ---------------------------------------------------------------------------

export function useMe() {
  const token = getToken();

  return useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    enabled: Boolean(token),
    retry: false,
  });
}

// ---------------------------------------------------------------------------
// useLogout
// ---------------------------------------------------------------------------

export function useLogout() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return () => {
    removeToken();
    queryClient.clear();
    void navigate("/login");
  };
}
