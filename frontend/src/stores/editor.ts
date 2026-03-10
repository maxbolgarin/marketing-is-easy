import { create } from "zustand";

export type EditorTab = "content" | "platforms" | "schedule" | "history";

interface EditorState {
  isOpen: boolean;
  postId: string | null;
  activeTab: EditorTab;
}

interface EditorActions {
  openEditor: (postId: string) => void;
  closeEditor: () => void;
  setActiveTab: (tab: EditorTab) => void;
}

export const useEditorStore = create<EditorState & EditorActions>((set) => ({
  // State
  isOpen: false,
  postId: null,
  activeTab: "content",

  // Actions
  openEditor: (postId) => set({ isOpen: true, postId, activeTab: "content" }),

  closeEditor: () => set({ isOpen: false, postId: null }),

  setActiveTab: (tab) => set({ activeTab: tab }),
}));
