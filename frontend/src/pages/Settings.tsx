import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  Loader2,
  RefreshCw,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  RotateCcw,
  Save,
  Circle,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import PlatformIcon from "@/components/shared/PlatformIcon";
import { useChannels, useTestChannel, useUpdateChannel } from "@/hooks/useChannels";
import { useSettings, useUpdateSettings, useDeleteSetting, useHealth } from "@/hooks/useSettings";
import { useMe } from "@/hooks/useAuth";
import { PLATFORM_LABELS } from "@/lib/constants";
import { formatDate } from "@/lib/date";
import { cn } from "@/lib/utils";
import type { SettingsGroup } from "@/api/settings";

export default function Settings() {
  const { data: me } = useMe();
  const { data: channels, isLoading: channelsLoading } = useChannels();
  const updateChannel = useUpdateChannel();
  const testChannel = useTestChannel();

  return (
    <div className="flex flex-col gap-8 p-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground mt-0.5">
          Manage your account, integrations, and API keys.
        </p>
      </div>

      {/* Service Status */}
      <ServiceStatus />

      {/* Brand / Account */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Brand Profile
        </h2>
        <div className="rounded-xl border border-border bg-card px-4 py-3 flex flex-col gap-3">
          {me ? (
            <>
              <Row label="Username" value={me.username} />
              {me.display_name && <Row label="Display Name" value={me.display_name} />}
              <Row label="Account ID" value={<span className="font-mono text-xs">{me.id}</span>} />
              <Row
                label="Status"
                value={
                  me.is_active ? (
                    <span className="flex items-center gap-1 text-emerald-400">
                      <CheckCircle2 className="size-3.5" />
                      Active
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-red-400">
                      <XCircle className="size-3.5" />
                      Inactive
                    </span>
                  )
                }
              />
              <Row label="Member since" value={formatDate(me.created_at)} />
            </>
          ) : (
            <div className="flex flex-col gap-2">
              <Skeleton className="h-4 w-48" />
              <Skeleton className="h-4 w-32" />
            </div>
          )}
        </div>
      </section>

      {/* Connected Accounts */}
      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          Connected Accounts
        </h2>

        {channelsLoading && (
          <div className="flex flex-col gap-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full rounded-xl" />
            ))}
          </div>
        )}

        {!channelsLoading && (!channels || channels.length === 0) && (
          <div className="rounded-xl border border-dashed border-border px-4 py-8 text-center">
            <p className="text-sm text-muted-foreground">
              No channels connected yet.
            </p>
          </div>
        )}

        {channels && channels.length > 0 && (
          <div className="flex flex-col gap-2">
            {channels.map((channel) => {
              const isTesting =
                testChannel.isPending && testChannel.variables === channel.id;

              return (
                <div
                  key={channel.id}
                  className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3"
                >
                  <PlatformIcon platform={channel.platform} className="size-5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">
                      {PLATFORM_LABELS[channel.platform] ?? channel.platform}
                    </p>
                    <p className="text-xs text-muted-foreground truncate">
                      {channel.account_name ?? channel.track}
                    </p>
                    {channel.token_expires_at && (
                      <p className="text-xs text-muted-foreground">
                        Token expires: {formatDate(channel.token_expires_at)}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span
                      className={cn(
                        "text-xs px-2 py-0.5 rounded-full font-medium",
                        channel.is_active
                          ? "bg-emerald-950 text-emerald-400"
                          : "bg-muted text-muted-foreground",
                      )}
                    >
                      {channel.is_active ? "Active" : "Inactive"}
                    </span>

                    <Button
                      variant="ghost"
                      size="icon-sm"
                      title="Test connection"
                      disabled={isTesting}
                      onClick={() => testChannel.mutate(channel.id)}
                    >
                      {isTesting ? (
                        <Loader2 className="size-3.5 animate-spin" />
                      ) : (
                        <RefreshCw className="size-3.5" />
                      )}
                    </Button>

                    <button
                      role="switch"
                      aria-checked={channel.is_active}
                      onClick={() =>
                        updateChannel.mutate({
                          id: channel.id,
                          data: { is_active: !channel.is_active },
                        })
                      }
                      className={cn(
                        "relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200",
                        channel.is_active ? "bg-primary" : "bg-muted",
                      )}
                    >
                      <span
                        className={cn(
                          "pointer-events-none inline-block size-4 rounded-full bg-white shadow-lg transition-transform duration-200",
                          channel.is_active ? "translate-x-4" : "translate-x-0",
                        )}
                      />
                      <span className="sr-only">
                        {channel.is_active ? "Disable" : "Enable"} channel
                      </span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Configuration */}
      <ConfigurationSection />
    </div>
  );
}

// ---------------------------------------------------------------------------
// Service Status
// ---------------------------------------------------------------------------

function ServiceStatus() {
  const { data: health, isLoading } = useHealth();

  if (isLoading || !health) return null;

  const services = health.services ?? {};
  const entries = Object.entries(services);
  if (entries.length === 0) return null;

  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
        Service Status
      </h2>
      <div className="rounded-xl border border-border bg-card px-4 py-3">
        <div className="flex flex-wrap gap-3">
          {entries.map(([name, status]) => (
            <div key={name} className="flex items-center gap-1.5">
              <Circle
                className={cn(
                  "size-2.5 fill-current",
                  status === "running" ? "text-emerald-400" : "text-red-400",
                )}
              />
              <span className="text-xs text-muted-foreground">{name.replace(/_/g, " ")}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ---------------------------------------------------------------------------
// Configuration Section (API Keys & Settings)
// ---------------------------------------------------------------------------

function ConfigurationSection() {
  const { data: groups, isLoading } = useSettings();

  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
        Configuration
      </h2>

      {isLoading && (
        <div className="flex flex-col gap-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-14 w-full rounded-xl" />
          ))}
        </div>
      )}

      {groups && groups.map((group) => (
        <SettingsGroupCard key={group.group} group={group} />
      ))}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Settings Group Card
// ---------------------------------------------------------------------------

function SettingsGroupCard({ group }: { group: SettingsGroup }) {
  const [expanded, setExpanded] = useState(false);
  const [dirty, setDirty] = useState<Record<string, string>>({});
  const [revealed, setRevealed] = useState<Set<string>>(new Set());
  const updateSettings = useUpdateSettings();
  const deleteSetting = useDeleteSetting();

  const hasDirty = Object.keys(dirty).length > 0;

  function handleChange(key: string, value: string) {
    setDirty((prev) => ({ ...prev, [key]: value }));
  }

  function handleSave() {
    if (!hasDirty) return;
    updateSettings.mutate(dirty, {
      onSuccess: () => setDirty({}),
    });
  }

  function handleRevert(key: string) {
    deleteSetting.mutate(key);
    setDirty((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }

  function toggleReveal(key: string) {
    setRevealed((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full px-4 py-3 text-left hover:bg-muted/50 transition-colors"
      >
        <span className="text-sm font-medium">{group.label}</span>
        <div className="flex items-center gap-2">
          {hasDirty && (
            <span className="text-xs text-yellow-400">unsaved</span>
          )}
          {expanded ? (
            <ChevronDown className="size-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="size-4 text-muted-foreground" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="border-t border-border px-4 py-3 flex flex-col gap-3">
          {group.settings.map((setting) => {
            const isRevealed = revealed.has(setting.key);
            const currentValue = dirty[setting.key] ?? setting.value;
            const isDirty = setting.key in dirty;

            return (
              <div key={setting.key} className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <label className="text-xs text-muted-foreground flex-1">
                    {setting.label}
                  </label>
                  <SourceBadge source={setting.source} />
                  {setting.source === "database" && (
                    <button
                      onClick={() => handleRevert(setting.key)}
                      title="Revert to environment default"
                      className="text-muted-foreground hover:text-foreground transition-colors"
                    >
                      <RotateCcw className="size-3" />
                    </button>
                  )}
                </div>
                <div className="flex items-center gap-1.5">
                  <input
                    type={setting.is_secret && !isRevealed ? "password" : "text"}
                    value={currentValue}
                    onChange={(e) => handleChange(setting.key, e.target.value)}
                    placeholder={setting.is_secret ? "Enter value..." : "Not set"}
                    className={cn(
                      "flex-1 rounded-md border border-border bg-background px-2.5 py-1.5 text-sm outline-none focus:ring-1 focus:ring-ring",
                      isDirty && "border-yellow-500/50",
                    )}
                  />
                  {setting.is_secret && (
                    <button
                      onClick={() => toggleReveal(setting.key)}
                      className="text-muted-foreground hover:text-foreground transition-colors p-1"
                    >
                      {isRevealed ? <EyeOff className="size-3.5" /> : <Eye className="size-3.5" />}
                    </button>
                  )}
                </div>
              </div>
            );
          })}

          {hasDirty && (
            <div className="flex justify-end pt-1">
              <Button
                size="sm"
                onClick={handleSave}
                disabled={updateSettings.isPending}
              >
                {updateSettings.isPending ? (
                  <Loader2 className="size-3.5 animate-spin mr-1.5" />
                ) : (
                  <Save className="size-3.5 mr-1.5" />
                )}
                Save
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Source Badge
// ---------------------------------------------------------------------------

function SourceBadge({ source }: { source: string }) {
  const styles: Record<string, string> = {
    database: "bg-blue-950 text-blue-400",
    environment: "bg-emerald-950 text-emerald-400",
    default: "bg-muted text-muted-foreground",
  };
  const labels: Record<string, string> = {
    database: "DB",
    environment: "ENV",
    default: "default",
  };
  return (
    <span className={cn("text-[10px] px-1.5 py-0.5 rounded font-medium", styles[source])}>
      {labels[source] ?? source}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Row helper
// ---------------------------------------------------------------------------

function Row({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <span className="text-xs text-muted-foreground shrink-0">{label}</span>
      <span className="text-sm text-right">{value}</span>
    </div>
  );
}
