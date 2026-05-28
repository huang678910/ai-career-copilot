"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";
import { ResumeList } from "@/components/resume/ResumeList";
import { ResumeUpload } from "@/components/resume/ResumeUpload";
import type { Resume } from "@/types/resume";

export default function ResumesPage() {
  const router = useRouter();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [showImport, setShowImport] = useState(false);

  const fetchResumes = useCallback(async () => {
    try {
      const { data } = await apiClient.get(API_ENDPOINTS.resumes);
      setResumes(data);
    } catch (err) {
      console.error("Failed to fetch resumes:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchResumes();
  }, [fetchResumes]);

  const handleCreate = async () => {
    try {
      const { data } = await apiClient.post(API_ENDPOINTS.resumes, {
        title: "我的简历",
        language: "zh",
      });
      router.push(`/resumes/${data.id}`);
    } catch (err) {
      setError("创建简历失败，请重试");
      setTimeout(() => setError(""), 3000);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("确定要删除这个简历吗？此操作不可撤销。")) return;
    try {
      await apiClient.delete(`${API_ENDPOINTS.resumes}/${id}`);
      setResumes(resumes.filter((r) => r.id !== id));
    } catch (err) {
      setError("删除失败，请重试");
      setTimeout(() => setError(""), 3000);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">简历管理</h1>
          <p className="text-sm text-muted-foreground mt-1">
            创建和管理您的简历，使用 AI 助手优化简历内容
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={() => setShowImport(true)}>
          <Upload className="mr-1 h-4 w-4" />
          导入简历
        </Button>
      </div>
      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive">
          {error}
        </div>
      )}
      <ResumeList resumes={resumes} isLoading={isLoading} onCreate={handleCreate} onDelete={handleDelete} />
      {showImport && <ResumeUpload onClose={() => { setShowImport(false); fetchResumes(); }} />}
    </div>
  );
}
