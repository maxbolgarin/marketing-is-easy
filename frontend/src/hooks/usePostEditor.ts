import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router";

import { useEditorStore } from "@/stores/editor";

// ---------------------------------------------------------------------------
// usePostEditor
// Combines useEditorStore with URL sync:
//   - When editor opens  → adds  ?post=<id> to the current URL
//   - When editor closes → removes ?post= from the URL
//   - On mount           → if ?post= is present, opens the editor with that id
// ---------------------------------------------------------------------------

export function usePostEditor() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const { isOpen, postId, scheduledDate, activeTab, openEditor, closeEditor, setActiveTab } =
    useEditorStore();

  // On mount: sync URL → store
  useEffect(() => {
    const idFromUrl = searchParams.get("post");
    if (idFromUrl && !isOpen) {
      openEditor(idFromUrl);
    }
    // Run only on mount — intentional omission of reactive deps
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync store → URL whenever isOpen / postId changes
  useEffect(() => {
    if (isOpen && postId) {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          next.set("post", postId);
          return next;
        },
        { replace: true },
      );
    } else {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          next.delete("post");
          return next;
        },
        { replace: true },
      );
    }
  }, [isOpen, postId, setSearchParams]);

  // Wrap closeEditor to also handle any imperative navigation needs
  const handleClose = () => {
    closeEditor();
  };

  // Wrap openEditor — consumers call this instead of the raw store action
  const handleOpen = (id: string, scheduledDate?: string) => {
    openEditor(id, scheduledDate);
  };

  return {
    isOpen,
    postId,
    scheduledDate,
    activeTab,
    openEditor: handleOpen,
    closeEditor: handleClose,
    setActiveTab,
    navigate,
  };
}
