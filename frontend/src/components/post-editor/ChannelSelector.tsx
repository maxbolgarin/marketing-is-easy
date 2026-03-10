import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PlatformIcon } from "@/components/shared/PlatformIcon";
import { PLATFORM_LABELS } from "@/lib/constants";
import { useChannels } from "@/hooks/useChannels";
import type { Channel } from "@/lib/types";

interface ChannelSelectorProps {
  value: string | null;
  onChange: (channelId: string, channel: Channel) => void;
}

export default function ChannelSelector({
  value,
  onChange,
}: ChannelSelectorProps) {
  const { data: channels, isLoading } = useChannels();

  if (isLoading) return <Skeleton className="h-9 w-full" />;

  const activeChannels = (channels ?? []).filter((c) => c.is_active);

  return (
    <Select
      value={value ?? ""}
      onValueChange={(channelId: string) => {
        const channel = activeChannels.find((c) => c.id === channelId);
        if (channel) onChange(channelId, channel);
      }}
    >
      <SelectTrigger className="w-full h-9">
        <SelectValue placeholder="Select connection..." />
      </SelectTrigger>
      <SelectContent align="start" alignItemWithTrigger={false}>
        {activeChannels.map((channel) => (
          <SelectItem key={channel.id} value={channel.id}>
            <PlatformIcon platform={channel.platform} className="size-4" />
            <span>
              {channel.account_name ||
                PLATFORM_LABELS[channel.platform] ||
                channel.platform}
            </span>
          </SelectItem>
        ))}
        {activeChannels.length === 0 && (
          <div className="px-2 py-4 text-xs text-center text-muted-foreground">
            No active channels configured
          </div>
        )}
      </SelectContent>
    </Select>
  );
}
