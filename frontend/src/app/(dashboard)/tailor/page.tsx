"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { ChevronRight, GitCompare, Loader2, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MatchScoreGauge } from "@/components/tailor/MatchScoreGauge";
import { SkillGapList } from "@/components/tailor/SkillGapList";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";
import type { Resume } from "@/types/resume";

export default function TailorPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [tailored, setTailored] = useState<any[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [selectedAnalysisId, setSelectedAnalysisId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    try {
      const [resData, anaData, tailData] = await Promise.all([
        apiClient.get(API_ENDPOINTS.resumes).catch(() => ({ data: [] })),
        apiClient.get(API_ENDPOINTS.jdAnalysis).catch(() => ({ data: [] })),
        apiClient.get(API_ENDPOINTS.tailor).catch(() => ({ data: [] })),
      ]);
      setResumes(resData.data || []);
      setAnalyses(anaData.data || []);
      setTailored(tailData.data || []);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleTailor = async () => {
    if (!selectedResumeId || !selectedAnalysisId) return;
    setIsLoading(true);
    setError("");
    setResult(null);
    try {
      const { data } = await apiClient.post(API_ENDPOINTS.tailor, {
        source_resume_id: selectedResumeId,
        jd_analysis_id: selectedAnalysisId,
      }, { timeout: 120000 });
      setResult(data);
      fetchData();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "定制失败，请检查后端服务是否正常");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">简历定制</h1>
        <p className="text-sm text-muted-foreground mt-1">根据 JD 智能优化简历，提升 ATS 匹配度</p>
      </div>

      {error && <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive">{error}</div>}

      <Card>
        <CardHeader><CardTitle className="text-base">选择简历和 JD 分析</CardTitle></CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            <select className="w-full rounded-md border px-3 py-2 text-sm" value={selectedResumeId} onChange={(e) => setSelectedResumeId(e.target.value)}>
              <option value="">-- 选择简历 --</option>
              {resumes.map((r) => <option key={r.id} value={r.id}>{r.title}</option>)}
            </select>
            <select className="w-full rounded-md border px-3 py-2 text-sm" value={selectedAnalysisId} onChange={(e) => setSelectedAnalysisId(e.target.value)}>
              <option value="">-- 选择 JD 分析 --</option>
              {analyses.map((a: any) => <option key={a.id} value={a.id}>{a.position_title || "未命名"} ({new Date(a.created_at).toLocaleDateString("zh-CN")})</option>)}
            </select>
          </div>
          <Button className="mt-4" onClick={handleTailor} disabled={isLoading || !selectedResumeId || !selectedAnalysisId}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isLoading ? "AI 优化中..." : "开始定制优化"}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="lg:col-span-1">
            <CardHeader><CardTitle className="text-base">匹配评分</CardTitle></CardHeader>
            <CardContent className="flex flex-col items-center gap-4">
              <MatchScoreGauge score={result.match_score} />
              <SkillGapList gaps={result.skill_gaps} matches={result.optimized_content?.skill_matches} />
            </CardContent>
          </Card>
          <Card className="lg:col-span-2">
            <CardHeader><CardTitle className="text-base">优化建议</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              {result.tailoring_notes && (
                <div className="rounded-lg bg-muted p-4 text-sm">
                  <p className="font-medium mb-1">AI 分析备注</p>
                  <p className="text-muted-foreground whitespace-pre-wrap">{result.tailoring_notes}</p>
                </div>
              )}
              {result.optimized_content?.optimized_summary && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold">优化后的个人总结</h4>
                  <p className="rounded border p-3 text-sm">{result.optimized_content.optimized_summary}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {tailored.length > 0 && (
        <Card>
          <CardHeader><CardTitle className="text-base">定制历史</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {tailored.map((t: any) => (
              <Link key={t.id} href={`/tailor/${t.id}`} className="flex items-center justify-between rounded-lg border p-3 text-sm hover:bg-accent transition-colors">
                <div className="flex items-center gap-3">
                  <GitCompare className="h-4 w-4 text-muted-foreground" />
                  <span>版本 {t.version}</span>
                  {t.match_score && <Badge variant={t.match_score >= 70 ? "success" : t.match_score >= 50 ? "warning" : "destructive"}>{Math.round(t.match_score)}%</Badge>}
                  <Trash2 className="h-4 w-4 text-muted-foreground hover:text-destructive shrink-0"
                    onClick={async (e) => { e.preventDefault(); e.stopPropagation(); if (!confirm("确定删除？")) return; try { await apiClient.delete(`${API_ENDPOINTS.tailor}/${t.id}`); fetchData(); } catch {} }} />
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </Link>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
