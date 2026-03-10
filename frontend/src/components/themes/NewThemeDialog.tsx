import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useCreateTheme } from "@/hooks/useTheme";
import { PLATFORM_LABELS } from "@/lib/constants";
import type { Platform } from "@/lib/types";

const PLATFORMS: { value: Platform; label: string }[] = [
  { value: "telegram", label: PLATFORM_LABELS.telegram },
  { value: "instagram_post", label: PLATFORM_LABELS.instagram_post },
  { value: "instagram_reel", label: PLATFORM_LABELS.instagram_reel },
  { value: "youtube_short", label: PLATFORM_LABELS.youtube_short },
  { value: "twitter", label: PLATFORM_LABELS.twitter },
];

const COLORS = [
  "#3B82F6",
  "#10B981",
  "#F59E0B",
  "#EF4444",
  "#8B5CF6",
  "#EC4899",
  "#06B6D4",
  "#F97316",
];

interface NewThemeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function NewThemeDialog({
  open,
  onOpenChange,
}: NewThemeDialogProps) {
  const createTheme = useCreateTheme();

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [cadenceType, setCadenceType] = useState("manual");
  const [color, setColor] = useState(COLORS[0]);
  const [selectedPlatforms, setSelectedPlatforms] = useState<Platform[]>([]);

  function reset() {
    setName("");
    setDescription("");
    setCadenceType("manual");
    setColor(COLORS[0]);
    setSelectedPlatforms([]);
  }

  function togglePlatform(p: Platform) {
    setSelectedPlatforms((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p],
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;

    await createTheme.mutateAsync({
      name: name.trim(),
      description: description.trim() || undefined,
      target_platforms: selectedPlatforms,
      cadence_type: cadenceType,
      cadence_rule: "",
      color,
      track: "eu",
    });
    reset();
    onOpenChange(false);
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>New Theme</DialogTitle>
            <DialogDescription>
              Create a content theme to organize your posts.
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col gap-4 py-4">
            {/* Name */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="theme-name" className="text-sm font-medium">
                Name <span className="text-destructive">*</span>
              </label>
              <Input
                id="theme-name"
                placeholder="e.g. Weekly Tips"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            {/* Description */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="theme-desc" className="text-sm font-medium">
                Description
              </label>
              <Textarea
                id="theme-desc"
                placeholder="What is this theme about?"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
              />
            </div>

            {/* Cadence */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">Cadence</label>
              <Select value={cadenceType} onValueChange={(v) => v && setCadenceType(v)}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="manual">Manual</SelectItem>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Platforms */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">Target Platforms</label>
              <div className="flex flex-wrap gap-2">
                {PLATFORMS.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => togglePlatform(value)}
                    className={`rounded-md border px-2.5 py-1 text-xs font-medium transition-colors ${
                      selectedPlatforms.includes(value)
                        ? "border-primary bg-primary/10 text-primary"
                        : "border-border text-muted-foreground hover:border-primary/50"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Color */}
            <div className="flex flex-col gap-1.5">
              <label className="text-sm font-medium">Color</label>
              <div className="flex gap-2">
                {COLORS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => setColor(c)}
                    className={`size-7 rounded-full transition-all ${
                      color === c
                        ? "ring-2 ring-ring ring-offset-2 ring-offset-background"
                        : "hover:scale-110"
                    }`}
                    style={{ backgroundColor: c }}
                    aria-label={`Color ${c}`}
                  />
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="submit"
              size="sm"
              disabled={!name.trim() || createTheme.isPending}
            >
              {createTheme.isPending ? "Creating..." : "Create Theme"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
