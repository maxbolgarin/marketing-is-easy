import { Outlet } from "react-router";
import Sidebar from "@/components/layout/Sidebar";
import SlideOverPanel from "@/components/layout/SlideOverPanel";
import { usePostEditor } from "@/hooks/usePostEditor";

export default function Layout() {
  const { isOpen, closeEditor } = usePostEditor();

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <Sidebar />

      <main className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto">
          <Outlet />
        </div>
      </main>

      {/* Post editor slide-over overlay */}
      <SlideOverPanel
        isOpen={isOpen}
        onClose={closeEditor}
        title="Edit Post"
      >
        {/* PostEditorPanel content will be rendered here by child routes */}
        <div className="p-5 text-sm text-muted-foreground">
          Post editor panel
        </div>
      </SlideOverPanel>
    </div>
  );
}
