"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { MessageSquare, Play, ChevronRight, Clock, BarChart3, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

const sessionTypeLabels: Record<string, string> = {
  technical: "技术面试",
  project_deep_dive: "项目深挖",
  hr: "HR 面试",
  stress: "压力面试",
};

const statusLabels: Record<string, string> = {
  in_progress: "进行中",
  completed: "已完成",
  cancelled: "已取消",
};

export default function MockInterviewPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<any[]>([]);
  const [resumes, setResumes] = useState<any[]>([]);
  const [resumeId, setResumeId] = useState("");
  const [sessionType, setSessionType] = useState("technical");
  const [questionCount, setQuestionCount] = useState(10);
  const [creating, setCreating] = useState(false);

  const fetchSessions = useCallback(async () => {
    try {
      const { data } = await apiClient.get(API_ENDPOINTS.interviewSessions);
      setSessions(data);
    } catch {}
  }, []);

  const fetchResumes = useCallback(async () => {
    try {
      const { data } = await apiClient.get(API_ENDPOINTS.resumes);
      setResumes(data || []);
    } catch {}
  }, []);

  useEffect(() => {
    fetchSessions();
    fetchResumes();
  }, [fetchSessions, fetchResumes]);

  const handleCreate = async () => {
    setCreating(true);
    try {
      const payload: any = {
        session_type: sessionType,
        questions_total: questionCount,
      };
      if (resumeId) payload.resume_id = resumeId;
      const { data } = await apiClient.post(API_ENDPOINTS.interviewSessions, payload);
      router.push(`/mock-interview/${data.id}`);
    } catch (err) {
      console.error("Create session failed:", err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">模拟面试</h1>
        <p className="text-sm text-muted-foreground mt-1">
          AI 实时模拟面试，选择简历生成个性化面试，支持综合评价与对话导出
        </p>
      </div>

      {/* New Session */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">开始新面试</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="text-sm font-medium">选择简历（可选）</label>
              <select className="mt-1 w-full rounded-md border px-3 py-2 text-sm" value={resumeId} onChange={(e) => setResumeId(e.target.value)}>
                <option value="">-- 通用面试 --</option>
                {resumes.map((r: any) => (
                  <option key={r.id} value={r.id}>{r.title || "未命名简历"}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">面试类型</label>
              <select className="mt-1 w-full rounded-md border px-3 py-2 text-sm" value={sessionType} onChange={(e) => setSessionType(e.target.value)}>
                {Object.entries(sessionTypeLabels).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">题目数量</label>
              <input type="number" min={3} max={30} value={questionCount} onChange={(e) => setQuestionCount(Number(e.target.value))} className="mt-1 w-full rounded-md border px-3 py-2 text-sm" />
            </div>
          </div>
          <Button className="mt-4" onClick={handleCreate} disabled={creating}>
            <Play className="mr-2 h-4 w-4" />
            {creating ? "创建中..." : "开始面试"}
          </Button>
        </CardContent>
      </Card>

      {/* Session History */}
      {sessions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">面试历史</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {sessions.map((s: any) => (
              <div
                key={s.id}
                className="flex items-center justify-between rounded-lg border p-3 text-sm hover:bg-accent cursor-pointer transition-colors"
                onClick={() => router.push(`/mock-interview/${s.id}`)}
              >
                <div className="flex items-center gap-3">
                  <MessageSquare className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <span className="font-medium">{sessionTypeLabels[s.session_type] || s.session_type}</span>
                    <div className="flex items-center gap-2 mt-0.5 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>{new Date(s.started_at).toLocaleString("zh-CN")}</span>
                      <span>·</span>
                      <span>{s.questions_asked}/{s.questions_total} 题</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {s.status === "completed" && s.overall_score && (
                    <Badge variant="outline" style={{
                      color: +(s.overall_score) >= 70 ? "#16a34a" : +(s.overall_score) >= 50 ? "#d97706" : "#dc2626",
                      borderColor: +(s.overall_score) >= 70 ? "#16a34a" : +(s.overall_score) >= 50 ? "#d97706" : "#dc2626"
                    }}>
                      <BarChart3 className="mr-1 h-3 w-3" />
                      {Math.round(s.overall_score)}分
                    </Badge>
                  )}
                  <Badge variant={s.status === "completed" ? "default" : s.status === "in_progress" ? "secondary" : "outline"}>
                    {statusLabels[s.status] || s.status}
                  </Badge>
                  <Trash2 className="h-4 w-4 text-muted-foreground hover:text-destructive" onClick={async (e) => {
                    e.stopPropagation();
                    if (!confirm("确定删除这条面试记录？")) return;
                    try { await apiClient.delete(`${API_ENDPOINTS.interviewSessions}/${s.id}`); fetchSessions(); } catch {}
                  }} />
                  <ChevronRight className="h-4 w-4 text-muted-foreground" />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
