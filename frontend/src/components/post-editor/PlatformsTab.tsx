import { Layers } from "lucide-react";

import { updateVariant } from "@/api/posts";
import type { UpdateVariantData } from "@/api/posts";
import type { Post } from "@/lib/types";
import PlatformVariantCard from "./PlatformVariantCard";

interface PlatformsTabProps {
  post: Post;
}

export default function PlatformsTab({ post }: PlatformsTabProps) {
  const publications = post.publications ?? [];

  async function handleVariantUpdate(
    variantId: string,
    data: UpdateVariantData,
  ) {
    await updateVariant(post.id, variantId, data);
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-start gap-2 rounded-lg bg-muted/30 border border-border px-3 py-2.5">
        <Layers className="size-4 text-muted-foreground mt-0.5 shrink-0" />
        <p className="text-xs text-muted-foreground leading-relaxed">
          Auto-adapted from your content brief. Each platform variant can be
          edited independently.
        </p>
      </div>

      {publications.length === 0 ? (
        <div className="flex flex-col items-center justify-center gap-2 py-12 text-muted-foreground">
          <Layers className="size-8 opacity-40" />
          <p className="text-sm">No platform variants yet.</p>
          <p className="text-xs opacity-70">
            Generate content first to create variants.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {publications.map((pub) => (
            <PlatformVariantCard
              key={pub.id}
              publication={pub}
              onUpdate={(data) =>
                void handleVariantUpdate(pub.id, {
                  platform_text: data.platform_text,
                  status: data.is_enabled === false ? "rejected" : undefined,
                })
              }
            />
          ))}
        </div>
      )}
    </div>
  );
}
