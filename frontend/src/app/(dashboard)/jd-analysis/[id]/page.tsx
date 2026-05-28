"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TechStackBadges } from "@/components/jd-analysis/TechStackBadges";
import { DifficultyMeter } from "@/components/jd-analysis/DifficultyMeter";
import { RiskFlags } from "@/components/jd-analysis/RiskFlags";
import { ImplicitReqs } from "@/components/jd-analysis/ImplicitReqs";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

export default function JDAnalysisDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [analysis, setAnalysis] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get(`${API_ENDPOINTS.jdAnalysis}/${params.id}`)
      .then(({ data }) => setAnalysis(data))
      .catch(() => router.push("/jd-analysis"))
      .finally(() => setIsLoading(false));
  }, [params.id, router]);

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!analysis) return null;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/jd-analysis")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-xl font-bold">{analysis.position_title || "JD 分析详情"}</h1>
          <p className="text-sm text-muted-foreground">
            {new Date(analysis.created_at).toLocaleString("zh-CN")}
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">技术栈</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <TechStackBadges techStack={analysis.tech_stack} />
              <DifficultyMeter score={analysis.difficulty_score} />
              <ImplicitReqs requirements={analysis.implicit_requirements} />
            </CardContent>
          </Card>
          <RiskFlags flags={analysis.risk_flags} riskScore={analysis.risk_score} />
        </div>

        <div className="space-y-6">
          {analysis.keywords && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base">关键词</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {analysis.keywords.map((kw: any, i: number) => (
                    <Badge
                      key={i}
                      variant={kw.weight >= 4 ? "default" : kw.weight >= 3 ? "secondary" : "outline"}
                    >
                      {kw.word} ({kw.weight})
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle className="text-base">原始 JD 文本</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap text-sm text-muted-foreground max-h-96 overflow-y-auto">
                {analysis.raw_text}
              </pre>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
