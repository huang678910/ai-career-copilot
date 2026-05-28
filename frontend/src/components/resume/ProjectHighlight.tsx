"use client";

import { useState } from "react";
import { Lightbulb, Loader2, Save, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

interface ProjectHighlightProps {
  resumeId: string;
  onSaved?: () => void;
}

export function ProjectHighlight({ resumeId, onSaved }: ProjectHighlightProps) {
  const [projectName, setProjectName] = useState("");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  const handleExtract = async () => {
    if (!projectName.trim() || !description.trim()) return;
    setLoading(true);
    setError("");
    setSaved(false);
    try {
      const { data } = await apiClient.post("/api/v1/resumes/ai/highlights", {
        project_name: projectName.trim(),
        description: description.trim(),
      });
      setResult(data.result);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "提取失败，请重试");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToResume = async () => {
    if (!result) return;
    setSaving(true);
    try {
      await apiClient.put(API_ENDPOINTS.resumeDetail(resumeId), { summary: result });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
      onSaved?.();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "保存失败");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-3 rounded-lg border p-4">
      <div className="flex items-center gap-2">
        <Lightbulb className="h-4 w-4 text-amber-500" />
        <span className="text-sm font-medium">项目亮点提取</span>
      </div>
      <Input
        value={projectName}
        onChange={(e) => setProjectName(e.target.value)}
        placeholder="项目名称"
      />
      <Textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="项目描述..."
        rows={3}
      />
      <Button size="sm" onClick={handleExtract} disabled={loading || !projectName.trim() || !description.trim()}>
        {loading && <Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" />}
        提取亮点
      </Button>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {result && (
        <div className="space-y-2">
          <div className="rounded bg-muted p-3 text-sm whitespace-pre-wrap">{result}</div>
          <Button size="sm" variant="outline" onClick={handleSaveToResume} disabled={saving || saved}>
            {saving && <Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" />}
            {saved ? <Check className="mr-1 h-3.5 w-3.5 text-emerald-500" /> : <Save className="mr-1 h-3.5 w-3.5" />}
            {saved ? "已保存" : "保存到简历"}
          </Button>
        </div>
      )}
    </div>
  );
}
