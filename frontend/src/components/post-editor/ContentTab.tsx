import { CheckCheck, Send } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useApprovePost, useUpdatePost } from "@/hooks/usePost";
import type { Post } from "@/lib/types";
import ImageSection from "./ImageSection";
import TextSection from "./TextSection";
import VideoSection from "./VideoSection";

interface ContentTabProps {
  post: Post;
}

export default function ContentTab({ post }: ContentTabProps) {
  const updatePost = useUpdatePost();
  const approvePost = useApprovePost();

  const platform = post.publications?.[0]?.platform;

  function handleUpdate(data: Parameters<typeof updatePost.mutate>[0]["data"]) {
    updatePost.mutate({ id: post.id, data });
  }

  const canApprove = post.status === "review" || post.status === "draft";
  const isSending = approvePost.isPending || updatePost.isPending;

  return (
    <div className="flex flex-col gap-5 pb-4">
      <section className="flex flex-col gap-2">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide px-0.5">
          Text
        </h3>
        <TextSection
          post={post}
          platform={platform}
          onUpdate={(data) => handleUpdate(data)}
        />
      </section>

      <Separator />

      <section className="flex flex-col gap-2">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide px-0.5">
          Image
        </h3>
        <ImageSection
          post={post}
          onUpdate={(data) => handleUpdate(data)}
        />
      </section>

      <Separator />

      <section className="flex flex-col gap-2">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide px-0.5">
          Video
        </h3>
        <VideoSection
          post={post}
          onUpdate={(data) => handleUpdate(data)}
        />
      </section>

      <Separator />

      <div className="flex items-center justify-end gap-2 pt-1">
        <Button
          variant="outline"
          size="sm"
          disabled={isSending || post.status === "review"}
          onClick={() => handleUpdate({ status: "review" })}
          className="gap-1.5"
        >
          <Send className="size-3.5" />
          Send to Review
        </Button>
        <Button
          size="sm"
          disabled={!canApprove || isSending}
          onClick={() => approvePost.mutate({ id: post.id })}
          className="gap-1.5"
        >
          <CheckCheck className="size-3.5" />
          Mark as Final
        </Button>
      </div>
    </div>
  );
}
