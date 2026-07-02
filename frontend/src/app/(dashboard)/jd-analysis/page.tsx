"use client";

import { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { FileSearch, ChevronRight, RotateCcw, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { JDInputForm } from "@/components/jd-analysis/JDInputForm";
import { TechStackBadges } from "@/components/jd-analysis/TechStackBadges";
import { DifficultyMeter } from "@/components/jd-analysis/DifficultyMeter";
import { RiskFlags } from "@/components/jd-analysis/RiskFlags";
import { ImplicitReqs } from "@/components/jd-analysis/ImplicitReqs";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

interface JDAnalysis {
  id: string;
  position_title: string | null;
  company_type: string | null;
  tech_stack: Record<string, string[]> | null;
  keywords: { word: string; weight: number }[] | null;
  implicit_requirements: string[] | null;
  difficulty_score: number | null;
  risk_flags: { type: string; signal: string; severity: string }[] | null;
  risk_score: number | null;
  created_at: string;
}

export default function JDAnalysisPage() {
  const [result, setResult] = useState<JDAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<JDAnalysis[]>([]);
  const [clearTrigger, setClearTrigger] = useState(0);
  const [error, setError] = useState("");

  const fetchHistory = useCallback(async () => {
    try {
      const { data } = await apiClient.get(API_ENDPOINTS.jdAnalysis);
      setHistory(data);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const handleAnalyze = async (text: string) => {
    setIsLoading(true);
    setError("");
    try {
      const { data } = await apiClient.post(API_ENDPOINTS.jdAnalysis, { raw_text: text }, { timeout: 120000 });
      setResult(data);
      fetchHistory();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic validation error — extract messages
        setError(detail.map((e: any) => e.msg).join("; "));
      } else if (typeof detail === "string") {
        setError(detail);
      } else {
        setError("分析失败，请重试");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAnalysis = async (id: string, e: React.MouseEvent) => {
    e.preventDefault(); e.stopPropagation();
    if (!confirm("确定删除此分析？")) return;
    try {
      await apiClient.delete(`${API_ENDPOINTS.jdAnalysis}/${id}`);
      setHistory(history.filter((h) => h.id !== id));
    } catch {}
  };

  const handleReset = () => {
    setResult(null);
    setError("");
    setClearTrigger((c) => c + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">JD 分析</h1>
          <p className="text-sm text-muted-foreground mt-1">
            AI 智能分析职位描述，提取技术栈、评估难度、识别风险
          </p>
        </div>
        {result && (
          <Button variant="outline" size="sm" onClick={handleReset}>
            <RotateCcw className="mr-1 h-4 w-4" /> 新建分析
          </Button>
        )}
      </div>

      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive">{error}</div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">职位描述输入</CardTitle>
            </CardHeader>
            <CardContent>
              <JDInputForm onSubmit={handleAnalyze} isLoading={isLoading} clearTrigger={clearTrigger} />
            </CardContent>
          </Card>

          {history.length > 0 && (
            <Card className="mt-4">
              <CardHeader>
                <CardTitle className="text-base">分析历史</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {history.slice(0, 5).map((item) => (
                  <Link
                    key={item.id}
                    href={`/jd-analysis/${item.id}`}
                    className="flex items-center justify-between rounded-lg border p-3 text-sm hover:bg-accent transition-colors"
                  >
                    <div>
                      <span className="font-medium">
                        {item.position_title || "未命名职位"}
                      </span>
                      <span className="ml-2 text-xs text-muted-foreground">
                        {new Date(item.created_at).toLocaleDateString("zh-CN")}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {item.difficulty_score && (
                        <Badge variant="secondary">难度 {item.difficulty_score}/5</Badge>
                      )}
                      <Trash2 className="h-4 w-4 text-muted-foreground hover:text-destructive shrink-0"
                        onClick={(e) => handleDeleteAnalysis(item.id, e)} />
                      <ChevronRight className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </Link>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        <div>
          {result ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">
                      {result.position_title || "分析结果"}
                    </CardTitle>
                    {result.company_type && (
                      <Badge variant="outline">{result.company_type}</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <TechStackBadges techStack={result.tech_stack} />
                  <DifficultyMeter score={result.difficulty_score} />
                  <ImplicitReqs requirements={result.implicit_requirements} />
                </CardContent>
              </Card>

              <RiskFlags flags={result.risk_flags} riskScore={result.risk_score} />

              {result.keywords && result.keywords.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">关键词权重</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {result.keywords.map((kw, i) => (
                        <Badge key={i} variant={kw.weight >= 4 ? "default" : kw.weight >= 3 ? "secondary" : "outline"}>
                          {kw.word} ({kw.weight})
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="flex h-full min-h-[300px] items-center justify-center rounded-lg border border-dashed">
              <div className="text-center text-muted-foreground">
                <FileSearch className="mx-auto h-8 w-8" />
                <p className="mt-2 text-sm">在左侧粘贴 JD 开始分析</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
