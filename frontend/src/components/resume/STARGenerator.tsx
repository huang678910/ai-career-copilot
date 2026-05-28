"use client";

import { useState } from "react";
import { Sparkles, Copy, Check, Loader2, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";

interface STARGeneratorProps {
  resumeId: string;
  onSaved?: () => void;
}

export function STARGenerator({ resumeId, onSaved }: STARGeneratorProps) {
  const [input, setInput] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);

  const handleGenerate = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    setSaved(false);
    try {
      const { data } = await apiClient.post("/api/v1/resumes/ai/star", {
        description: input.trim(),
      });
      setResult(data.result);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "生成失败，请重试");
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
        <Sparkles className="h-4 w-4 text-amber-500" />
        <span className="text-sm font-medium">STAR 描述生成器</span>
      </div>
      <Textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="粘贴原始项目描述，AI 将转化为 STAR 格式..."
        rows={3}
      />
      <Button size="sm" onClick={handleGenerate} disabled={loading || !input.trim()}>
        {loading && <Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" />}
        {loading ? "生成中..." : "生成 STAR 描述"}
      </Button>
      {error && <p className="text-sm text-destructive">{error}</p>}
      {result && (
        <div className="space-y-2">
          <div className="relative rounded bg-muted p-3 text-sm">
            <p className="whitespace-pre-wrap">{result}</p>
            <button
              className="absolute right-2 top-2 rounded p-1 hover:bg-background"
              onClick={() => { navigator.clipboard.writeText(result); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
          </div>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={handleSaveToResume} disabled={saving || saved}>
              {saving && <Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" />}
              {saved ? <Check className="mr-1 h-3.5 w-3.5 text-emerald-500" /> : <Save className="mr-1 h-3.5 w-3.5" />}
              {saved ? "已保存" : "保存到简历"}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
