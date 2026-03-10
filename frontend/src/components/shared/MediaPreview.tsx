import { ImageIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface MediaPreviewProps {
  urls: string[] | null;
  mediaType: string | null;
  className?: string;
}

function Placeholder({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "flex items-center justify-center rounded-md bg-muted",
        className,
      )}
    >
      <ImageIcon className="size-8 text-muted-foreground" />
    </div>
  );
}

export default function MediaPreview({ urls, mediaType, className }: MediaPreviewProps) {
  const hasUrls = urls && urls.length > 0;

  if (!hasUrls || !mediaType || mediaType === "none") {
    return <Placeholder className={cn("aspect-square w-full", className)} />;
  }

  if (mediaType === "video") {
    return (
      <video
        src={urls[0]}
        controls
        className={cn("w-full rounded-md bg-black object-contain", className)}
        aria-label="Video preview"
      />
    );
  }

  if (mediaType === "carousel" && urls.length > 1) {
    return (
      <div className={cn("grid gap-1.5", className)}>
        <img
          src={urls[0]}
          alt="Preview 1"
          className="w-full rounded-md object-cover aspect-square"
          loading="lazy"
        />
        {urls.length > 1 && (
          <div className="grid grid-cols-3 gap-1.5">
            {urls.slice(1, 4).map((url, i) => (
              <div key={url} className="relative">
                <img
                  src={url}
                  alt={`Preview ${i + 2}`}
                  className="w-full rounded-md object-cover aspect-square"
                  loading="lazy"
                />
                {i === 2 && urls.length > 4 && (
                  <div className="absolute inset-0 flex items-center justify-center rounded-md bg-black/60">
                    <span className="text-sm font-medium text-white">
                      +{urls.length - 4}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // single image
  return (
    <img
      src={urls[0]}
      alt="Media preview"
      className={cn("w-full rounded-md object-cover", className)}
      loading="lazy"
    />
  );
}
