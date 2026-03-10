export const queryKeys = {
  posts: {
    all: ["posts"] as const,
    list: (f: unknown) => ["posts", "list", f] as const,
    detail: (id: string) => ["posts", id] as const,
  },
  themes: {
    all: ["themes"] as const,
    list: (f: unknown) => ["themes", "list", f] as const,
    detail: (id: string) => ["themes", id] as const,
  },
  calendar: (s: string, e: string) => ["calendar", s, e] as const,
  dashboard: {
    stats: ["dashboard", "stats"] as const,
    upcoming: ["dashboard", "upcoming"] as const,
    attention: ["dashboard", "attention"] as const,
  },
  channels: ["channels"] as const,
  settings: ["settings"] as const,
  health: ["health"] as const,
} as const;
