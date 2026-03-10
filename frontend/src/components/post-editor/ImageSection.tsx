import { useRef, useState } from "react";
import { ImageIcon, Loader2, RefreshCw, Upload, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useGenerateImage } from "@/hooks/useGeneration";
import type { Post } from "@/lib/types";
import { uploadAsset } from "@/api/assets";
import { cn } from "@/lib/utils";
import GenerateButton from "./GenerateButton";

type ImageMode = "none" | "upload" | "generate" | "template";

interface ImageSectionProps {
  post: Post;
  onUpdate: (data: Partial<Pick<Post, "media_urls" | "media_type">>) => void;
}

export default function ImageSection({ post, onUpdate }: ImageSectionProps) {
  const currentMode = (): ImageMode => {
    if (!post.media_type || post.media_type === "none") return "none";
    if (post.media_urls?.length) return "generate";
    return "none";
  };

  const [mode, setMode] = useState<ImageMode>(currentMode);
  const [prompt, setPrompt] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const generateImage = useGenerateImage();
  const isGenerating = generateImage.isPending;
  const imageUrl = post.media_urls?.[0];

  function handleGenerate() {
    generateImage.mutate({
      id: post.id,
      data: { prompt: prompt || undefined },
    });
  }

  function handleModeChange(next: ImageMode) {
    setMode(next);
    if (next === "none") {
      onUpdate({ media_type: "none", media_urls: [] });
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-1 rounded-lg bg-muted p-0.5 w-fit flex-wrap">
        {(["none", "upload", "generate", "template"] as ImageMode[]).map((m) => {
          const isDisabled = m === "template";
          return (
            <button
              key={m}
              onClick={() => !isDisabled && handleModeChange(m)}
              disabled={isDisabled}
              className={cn(
                "rounded-md px-3 py-1 text-xs font-medium capitalize transition-colors",
                mode === m
                  ? "bg-background text-foreground shadow-sm"
                  : isDisabled
                    ? "text-muted-foreground/40 cursor-not-allowed"
                    : "text-muted-foreground hover:text-foreground",
              )}
              title={isDisabled ? "Coming soon" : undefined}
            >
              {m}
            </button>
          );
        })}
      </div>

      {mode === "none" && (
        <p className="text-xs text-muted-foreground">No image for this post.</p>
      )}

      {mode === "upload" && (
        <div className="flex flex-col gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={async (e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              setIsUploading(true);
              setUploadError(null);
              try {
                const asset = await uploadAsset(file);
                onUpdate({ media_type: "image", media_urls: [asset.url] });
              } catch {
                setUploadError("Image upload failed. Please try again.");
              } finally {
                setIsUploading(false);
                e.target.value = "";
              }
            }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border bg-muted/20 px-6 py-10 text-sm text-muted-foreground transition-colors hover:border-foreground/30 hover:bg-muted/40 hover:text-foreground disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUploading ? (
              <>
                <Loader2 className="size-6 animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload className="size-6" />
                <span>Click to upload image</span>
                <span className="text-xs">PNG, JPG, WEBP up to 10MB</span>
              </>
            )}
          </button>
          {uploadError && (
            <p className="text-xs text-red-400">{uploadError}</p>
          )}
          {imageUrl && <ImagePreview url={imageUrl} onRemove={() => onUpdate({ media_urls: [], media_type: "none" })} />}
        </div>
      )}

      {mode === "generate" && (
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Image Prompt
            </label>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the image you want to generate..."
              className="min-h-[72px] resize-none text-sm"
            />
          </div>

          <div className="flex items-center gap-2">
            <GenerateButton
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
              label="Generate Image"
            />
            {imageUrl && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleGenerate}
                disabled={isGenerating}
                className="gap-1.5"
              >
                <RefreshCw className="size-3.5" />
                Regenerate
              </Button>
            )}
          </div>

          {generateImage.isError && (
            <p className="text-xs text-red-400 rounded-md bg-red-950/40 px-2.5 py-1.5">
              Generation failed: {generateImage.error instanceof Error ? generateImage.error.message : "Unknown error"}
            </p>
          )}

          {imageUrl && (
            <ImagePreview
              url={imageUrl}
              onRemove={() => onUpdate({ media_urls: [], media_type: "none" })}
              onReplace={() => {
                onUpdate({ media_urls: [], media_type: "none" });
                setPrompt("");
              }}
            />
          )}
        </div>
      )}

      {mode === "template" && (
        <div className="flex items-center justify-center rounded-xl border border-border bg-muted/20 px-6 py-10">
          <div className="flex flex-col items-center gap-2 text-muted-foreground">
            <ImageIcon className="size-8" />
            <p className="text-sm">Template selection coming soon</p>
          </div>
        </div>
      )}
    </div>
  );
}

interface ImagePreviewProps {
  url: string;
  onRemove: () => void;
  onReplace?: () => void;
}

function ImagePreview({ url, onRemove, onReplace }: ImagePreviewProps) {
  return (
    <div className="relative group rounded-xl overflow-hidden border border-border bg-muted/20">
      <img
        src={url}
        alt="Post image"
        className="w-full object-cover max-h-[280px]"
      />
      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
        {onReplace && (
          <Button variant="secondary" size="sm" onClick={onReplace}>
            Replace
          </Button>
        )}
        <Button variant="destructive" size="sm" onClick={onRemove}>
          <X className="size-3.5 mr-1" />
          Remove
        </Button>
      </div>
    </div>
  );
}
