import { useRef, useState } from "react";
import { Upload, VideoIcon } from "lucide-react";

import { useGenerateVideo } from "@/hooks/useGeneration";
import type { Post } from "@/lib/types";
import { cn } from "@/lib/utils";
import GenerateButton from "./GenerateButton";

type VideoMode = "none" | "upload" | "generate";

interface VideoSectionProps {
  post: Post;
  onUpdate: (data: Partial<Pick<Post, "media_urls" | "media_type">>) => void;
}

export default function VideoSection({ post, onUpdate }: VideoSectionProps) {
  const currentMode = (): VideoMode => {
    if (!post.media_type || post.media_type === "none") return "none";
    if (post.media_type === "video") return "generate";
    return "none";
  };

  const [mode, setMode] = useState<VideoMode>(currentMode);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const generateVideo = useGenerateVideo();
  const isGenerating = generateVideo.isPending || post.status === "generating";
  const videoUrl = post.media_urls?.[0];

  function handleModeChange(next: VideoMode) {
    setMode(next);
    if (next === "none") {
      onUpdate({ media_type: "none", media_urls: [] });
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-1 rounded-lg bg-muted p-0.5 w-fit">
        {(["none", "upload", "generate"] as VideoMode[]).map((m) => (
          <button
            key={m}
            onClick={() => handleModeChange(m)}
            className={cn(
              "rounded-md px-3 py-1 text-xs font-medium capitalize transition-colors",
              mode === m
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {m}
          </button>
        ))}
      </div>

      {mode === "none" && (
        <p className="text-xs text-muted-foreground">No video for this post.</p>
      )}

      {mode === "upload" && (
        <div className="flex flex-col gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (!file) return;
              const objectUrl = URL.createObjectURL(file);
              onUpdate({ media_type: "video", media_urls: [objectUrl] });
            }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border bg-muted/20 px-6 py-10 text-sm text-muted-foreground transition-colors hover:border-foreground/30 hover:bg-muted/40 hover:text-foreground"
          >
            <Upload className="size-6" />
            <span>Click to upload video</span>
            <span className="text-xs">MP4, MOV up to 500MB</span>
          </button>
          {videoUrl && <VideoPreview url={videoUrl} />}
        </div>
      )}

      {mode === "generate" && (
        <div className="flex flex-col gap-3">
          <div className="rounded-lg border border-border bg-muted/20 px-4 py-3">
            <p className="text-sm text-muted-foreground leading-relaxed">
              Generates a full video short using the AI pipeline: scene planning,
              image generation, motion clips, TTS narration, and final composition.
              This may take several minutes.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <GenerateButton
              onGenerate={() => generateVideo.mutate(post.id)}
              isGenerating={isGenerating}
              label="Generate Video"
            />
            {isGenerating && (
              <span className="text-xs text-blue-400 animate-pulse">
                Pipeline running...
              </span>
            )}
          </div>

          {videoUrl && <VideoPreview url={videoUrl} />}
        </div>
      )}
    </div>
  );
}

function VideoPreview({ url }: { url: string }) {
  return (
    <div className="relative rounded-xl overflow-hidden border border-border bg-muted/20">
      {url.startsWith("blob:") || url.startsWith("http") ? (
        <video
          src={url}
          controls
          className="w-full max-h-[320px] object-contain"
          aria-label="Post video preview"
        />
      ) : (
        <div className="flex flex-col items-center justify-center gap-2 py-10 text-muted-foreground">
          <VideoIcon className="size-8" />
          <p className="text-sm">Video ready</p>
          <p className="text-xs break-all px-4 text-center opacity-60">{url}</p>
        </div>
      )}
    </div>
  );
}
