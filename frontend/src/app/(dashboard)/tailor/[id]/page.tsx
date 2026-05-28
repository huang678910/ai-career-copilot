"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { MatchScoreGauge } from "@/components/tailor/MatchScoreGauge";
import { SkillGapList } from "@/components/tailor/SkillGapList";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

export default function TailorDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [detail, setDetail] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get(`${API_ENDPOINTS.tailor}/${params.id}`)
      .then(({ data }) => setDetail(data))
      .catch(() => router.push("/tailor"))
      .finally(() => setIsLoading(false));
  }, [params.id, router]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!detail) return null;

  const content = detail.optimized_content || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/tailor")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-xl font-bold">定制版本 {detail.version}</h1>
          <p className="text-sm text-muted-foreground">
            {new Date(detail.created_at).toLocaleString("zh-CN")}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base">匹配度</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center gap-4">
            <MatchScoreGauge score={detail.match_score} />
            <SkillGapList gaps={detail.skill_gaps} matches={content.skill_matches} />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">优化内容详情</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {detail.tailoring_notes && (
              <div className="rounded-lg bg-muted p-4 text-sm">
                <p className="font-medium mb-1">优化备注</p>
                <p className="text-muted-foreground whitespace-pre-wrap">{detail.tailoring_notes}</p>
              </div>
            )}

            {content.optimized_summary && (
              <div className="space-y-2">
                <h4 className="text-sm font-semibold">优化后的个人总结</h4>
                <p className="rounded border p-3 text-sm">{content.optimized_summary}</p>
              </div>
            )}

            {content.optimized_projects?.map((proj: any, i: number) => (
              <div key={i} className="space-y-2">
                <h4 className="text-sm font-semibold">{proj.name}</h4>
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">原文</p>
                    <p className="rounded bg-muted p-3 text-sm">{proj.original_description}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-1">优化后</p>
                    <p className="rounded border border-emerald-200 bg-emerald-50 p-3 text-sm dark:bg-emerald-950 dark:border-emerald-800">
                      {proj.optimized_description}
                    </p>
                  </div>
                </div>
                {proj.added_keywords?.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {proj.added_keywords.map((kw: string) => (
                      <Badge key={kw} variant="success">{kw}</Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
