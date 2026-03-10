import { Loader2, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

interface GenerateButtonProps {
  onGenerate: () => void;
  isGenerating: boolean;
  label?: string;
}

export default function GenerateButton({
  onGenerate,
  isGenerating,
  label = "Generate",
}: GenerateButtonProps) {
  return (
    <Button
      onClick={onGenerate}
      disabled={isGenerating}
      size="sm"
      className="gap-1.5"
    >
      {isGenerating ? (
        <>
          <Loader2 className="size-3.5 animate-spin" />
          Generating...
        </>
      ) : (
        <>
          <Sparkles className="size-3.5" />
          {label}
        </>
      )}
    </Button>
  );
}
