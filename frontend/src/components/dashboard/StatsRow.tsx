import { AlertCircle, Calendar, CheckCircle, Eye } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useDashboardStats } from "@/hooks/useDashboard";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  danger?: boolean;
}

function StatCard({ title, value, icon, danger }: StatCardProps) {
  return (
    <Card className="flex-1 min-w-0">
      <CardHeader className="pb-1">
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            {title}
          </CardTitle>
          <span className={cn("shrink-0 text-muted-foreground", danger && value > 0 && "text-red-400")}>
            {icon}
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <p
          className={cn(
            "text-2xl font-bold tabular-nums",
            danger && value > 0 ? "text-red-400" : "text-foreground",
          )}
        >
          {value}
        </p>
      </CardContent>
    </Card>
  );
}

function StatCardSkeleton() {
  return (
    <Card className="flex-1 min-w-0">
      <CardHeader className="pb-1">
        <Skeleton className="h-3 w-28" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-16" />
      </CardContent>
    </Card>
  );
}

export function StatsRow() {
  const { data, isLoading, isError } = useDashboardStats();

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3 sm:flex-row">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col gap-3 sm:flex-row">
        {[
          { title: "Scheduled This Week", icon: <Calendar className="size-4" /> },
          { title: "Pending Review", icon: <Eye className="size-4" /> },
          { title: "Published This Month", icon: <CheckCircle className="size-4" /> },
          { title: "Failed", icon: <AlertCircle className="size-4" />, danger: true },
        ].map(({ title, icon, danger }) => (
          <StatCard key={title} title={title} value={0} icon={icon} danger={danger} />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 sm:flex-row">
      <StatCard
        title="Scheduled This Week"
        value={data.scheduled_this_week}
        icon={<Calendar className="size-4" />}
      />
      <StatCard
        title="Pending Review"
        value={data.pending_review}
        icon={<Eye className="size-4" />}
      />
      <StatCard
        title="Published This Month"
        value={data.published_this_month}
        icon={<CheckCircle className="size-4" />}
      />
      <StatCard
        title="Failed"
        value={data.failed}
        icon={<AlertCircle className="size-4" />}
        danger
      />
    </div>
  );
}
