import { Outlet } from "react-router";
import Sidebar from "@/components/layout/Sidebar";
import PostEditorPanel from "@/components/post-editor/PostEditorPanel";

export default function Layout() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <Sidebar />

      <main className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto">
          <Outlet />
        </div>
      </main>

      <PostEditorPanel />
    </div>
  );
}
