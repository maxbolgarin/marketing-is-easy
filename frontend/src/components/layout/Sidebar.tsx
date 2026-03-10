import { NavLink } from "react-router";
import {
  LayoutDashboard,
  Calendar,
  Palette,
  FolderOpen,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Separator } from "@/components/ui/separator";
import PlatformIcon from "@/components/shared/PlatformIcon";
import { useUIStore } from "@/stores/ui";
import { cn } from "@/lib/utils";
import { PLATFORM_LABELS } from "@/lib/constants";
import type { Platform } from "@/lib/types";

const PLATFORMS: { key: Platform | "email"; label: string }[] = [
  { key: "telegram", label: PLATFORM_LABELS.telegram },
  { key: "instagram_post", label: "Instagram" },
  { key: "youtube_short", label: "YouTube" },
  { key: "twitter", label: PLATFORM_LABELS.twitter },
  { key: "email", label: "Email" },
];

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  collapsed: boolean;
  end?: boolean;
}

function NavItem({ to, icon, label, collapsed, end }: NavItemProps) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-3 rounded-md px-2.5 py-2 text-sm font-medium transition-colors",
          "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
          isActive && "bg-accent text-accent-foreground",
          collapsed && "justify-center px-2",
        )
      }
      title={collapsed ? label : undefined}
    >
      <span className="shrink-0">{icon}</span>
      {!collapsed && <span className="truncate">{label}</span>}
    </NavLink>
  );
}

export default function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore();

  return (
    <aside
      className={cn(
        "relative flex h-full flex-col border-r border-border bg-card transition-all duration-200",
        sidebarCollapsed ? "w-14" : "w-56",
      )}
      aria-label="Sidebar navigation"
    >
      {/* Logo / Brand */}
      <div
        className={cn(
          "flex h-14 items-center border-b border-border px-3 shrink-0",
          sidebarCollapsed ? "justify-center" : "gap-2.5",
        )}
      >
        <div className="size-7 rounded-md bg-primary shrink-0" />
        {!sidebarCollapsed && (
          <span className="text-sm font-semibold tracking-tight truncate">
            Marketing
          </span>
        )}
      </div>

      {/* Scrollable nav area */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden p-2 space-y-0.5">
        <NavItem
          to="/"
          end
          icon={<LayoutDashboard className="size-4" />}
          label="Dashboard"
          collapsed={sidebarCollapsed}
        />
        <NavItem
          to="/calendar"
          icon={<Calendar className="size-4" />}
          label="Calendar"
          collapsed={sidebarCollapsed}
        />
        <NavItem
          to="/themes"
          icon={<Palette className="size-4" />}
          label="Themes"
          collapsed={sidebarCollapsed}
        />
        <NavItem
          to="/library"
          icon={<FolderOpen className="size-4" />}
          label="Content Library"
          collapsed={sidebarCollapsed}
        />

        <Separator className="my-2" />

        {!sidebarCollapsed && (
          <p className="px-2.5 py-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground select-none">
            Channels
          </p>
        )}

        {PLATFORMS.map(({ key, label }) => (
          <NavItem
            key={key}
            to={`/channels/${key}`}
            icon={<PlatformIcon platform={key} className="size-4" />}
            label={label}
            collapsed={sidebarCollapsed}
          />
        ))}
      </nav>

      {/* Bottom: Settings + collapse toggle */}
      <div className="shrink-0 border-t border-border p-2 space-y-0.5">
        <NavItem
          to="/settings"
          icon={<Settings className="size-4" />}
          label="Settings"
          collapsed={sidebarCollapsed}
        />
        <button
          type="button"
          onClick={toggleSidebar}
          className={cn(
            "flex w-full items-center gap-3 rounded-md px-2.5 py-2 text-sm font-medium transition-colors",
            "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
            sidebarCollapsed && "justify-center px-2",
          )}
          aria-label={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <span className="shrink-0">
            {sidebarCollapsed ? (
              <ChevronRight className="size-4" />
            ) : (
              <ChevronLeft className="size-4" />
            )}
          </span>
          {!sidebarCollapsed && <span>Collapse</span>}
        </button>
      </div>
    </aside>
  );
}
