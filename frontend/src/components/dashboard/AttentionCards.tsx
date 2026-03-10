import { AlertCircle, Eye } from "lucide-react";
import { Link } from "react-router";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useAttention } from "@/hooks/useDashboard";

function AttentionCardSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-4 w-40" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-24" />
      </CardContent>
    </Card>
  );
}

export function AttentionCards() {
  const { data, isLoading, isError } = useAttention();

  if (isLoading) {
    return (
      <div className="grid gap-3 sm:grid-cols-2">
        <AttentionCardSkeleton />
        <AttentionCardSkeleton />
      </div>
    );
  }

  if (isError || !data) return null;

  const pendingCount = data.pending_review.length;
  const failedCount = data.failed.length;

  if (pendingCount === 0 && failedCount === 0) return null;

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {pendingCount > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Eye className="size-4 text-yellow-400" />
              <CardTitle>
                {pendingCount} {pendingCount === 1 ? "Post" : "Posts"} Pending Review
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <Link to="/calendar?status=review">
              <Button size="sm" variant="outline">Review All</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {failedCount > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertCircle className="size-4 text-red-400" />
              <CardTitle className="text-red-400">
                {failedCount} Failed {failedCount === 1 ? "Post" : "Posts"}
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <Link to="/calendar?status=failed">
              <Button size="sm" variant="destructive">View</Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
