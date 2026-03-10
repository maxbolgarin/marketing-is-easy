import { create } from "zustand";

export type EditorTab = "content" | "platforms" | "schedule" | "history";

interface EditorState {
  isOpen: boolean;
  postId: string | null;
  scheduledDate: string | null;
  activeTab: EditorTab;
}

interface EditorActions {
  openEditor: (postId: string, scheduledDate?: string) => void;
  closeEditor: () => void;
  setActiveTab: (tab: EditorTab) => void;
}

export const useEditorStore = create<EditorState & EditorActions>((set) => ({
  // State
  isOpen: false,
  postId: null,
  scheduledDate: null,
  activeTab: "content",

  // Actions
  openEditor: (postId, scheduledDate) =>
    set({ isOpen: true, postId, scheduledDate: scheduledDate ?? null, activeTab: "content" }),

  closeEditor: () => set({ isOpen: false, postId: null, scheduledDate: null }),

  setActiveTab: (tab) => set({ activeTab: tab }),
}));
