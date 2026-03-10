import { create } from "zustand";

export type CalendarView = "week" | "month";

export interface Filters {
  themes: string[];
  platforms: string[];
  statuses: string[];
}

interface UIState {
  sidebarCollapsed: boolean;
  calendarView: CalendarView;
  calendarDate: Date;
  filters: Filters;
}

interface UIActions {
  toggleSidebar: () => void;
  setCalendarView: (view: CalendarView) => void;
  setCalendarDate: (date: Date) => void;
  setFilters: (filters: Partial<Filters>) => void;
  resetFilters: () => void;
}

const DEFAULT_FILTERS: Filters = {
  themes: [],
  platforms: [],
  statuses: [],
};

export const useUIStore = create<UIState & UIActions>((set) => ({
  // State
  sidebarCollapsed: false,
  calendarView: "week",
  calendarDate: new Date(),
  filters: DEFAULT_FILTERS,

  // Actions
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  setCalendarView: (view) => set({ calendarView: view }),

  setCalendarDate: (date) => set({ calendarDate: date }),

  setFilters: (filters) =>
    set((state) => ({
      filters: { ...state.filters, ...filters },
    })),

  resetFilters: () => set({ filters: DEFAULT_FILTERS }),
}));
