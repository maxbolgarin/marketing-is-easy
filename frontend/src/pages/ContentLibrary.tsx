import { useRef, useState } from "react";
import { Upload, ImageIcon, VideoIcon, FileIcon, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getAssets, uploadAsset } from "@/api/assets";
import type { Asset } from "@/lib/types";

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function AssetIcon({ contentType }: { contentType: string }) {
  if (contentType.startsWith("image/"))
    return <ImageIcon className="size-5 text-muted-foreground" />;
  if (contentType.startsWith("video/"))
    return <VideoIcon className="size-5 text-muted-foreground" />;
  return <FileIcon className="size-5 text-muted-foreground" />;
}

function AssetCard({ asset }: { asset: Asset }) {
  const isImage = asset.content_type.startsWith("image/");
  const isVideo = asset.content_type.startsWith("video/");

  return (
    <div className="group flex flex-col gap-2 rounded-xl border border-border bg-card overflow-hidden transition-colors hover:ring-1 hover:ring-foreground/20">
      <div className="aspect-square bg-muted/30 flex items-center justify-center overflow-hidden">
        {isImage ? (
          <img
            src={asset.url}
            alt={asset.filename}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : isVideo ? (
          <video
            src={asset.url}
            className="w-full h-full object-cover"
            muted
            preload="metadata"
          />
        ) : (
          <AssetIcon contentType={asset.content_type} />
        )}
      </div>
      <div className="px-3 pb-3 flex flex-col gap-0.5">
        <p
          className="text-xs font-medium truncate"
          title={asset.filename}
        >
          {asset.filename}
        </p>
        <p className="text-[10px] text-muted-foreground">
          {formatBytes(asset.size)}
        </p>
      </div>
    </div>
  );
}

export default function ContentLibrary() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const assetsQuery = useQuery({
    queryKey: ["assets"],
    queryFn: getAssets,
  });

  const upload = useMutation({
    mutationFn: (file: File) => uploadAsset(file),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["assets"] });
      setUploadError(null);
    },
    onError: () => {
      setUploadError("Upload failed. Please try again.");
    },
  });

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    upload.mutate(file);
    // reset input so same file can be re-selected
    e.target.value = "";
  }

  const assets = assetsQuery.data ?? [];

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Content Library</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Your uploaded images and videos.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,video/*"
            className="hidden"
            onChange={handleFileChange}
            aria-label="Upload asset"
          />
          <Button
            size="sm"
            className="gap-1.5"
            disabled={upload.isPending}
            onClick={() => fileInputRef.current?.click()}
          >
            {upload.isPending ? (
              <>
                <Loader2 className="size-3.5 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="size-3.5" />
                Upload
              </>
            )}
          </Button>
        </div>
      </div>

      {uploadError && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {uploadError}
        </div>
      )}

      {assetsQuery.isLoading && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} className="aspect-square w-full rounded-xl" />
          ))}
        </div>
      )}

      {assetsQuery.isError && (
        <div className="flex items-center justify-center py-20">
          <p className="text-sm text-muted-foreground">
            Failed to load assets.
          </p>
        </div>
      )}

      {!assetsQuery.isLoading && assets.length === 0 && (
        <button
          onClick={() => fileInputRef.current?.click()}
          className="flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-border px-6 py-16 text-muted-foreground transition-colors hover:border-foreground/30 hover:text-foreground"
        >
          <Upload className="size-8" />
          <p className="text-sm">No assets yet. Click to upload.</p>
          <p className="text-xs">Images and videos supported</p>
        </button>
      )}

      {assets.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {assets.map((asset) => (
            <AssetCard key={asset.path} asset={asset} />
          ))}
        </div>
      )}
    </div>
  );
}
