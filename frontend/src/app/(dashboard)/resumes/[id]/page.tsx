"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { GuidedResumeChat } from "@/components/resume/GuidedResumeChat";
import { ResumePreview } from "@/components/resume/ResumePreview";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";
import { useResumeStore } from "@/stores/resume-store";

export default function ResumeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const resumeId = params.id as string;
  const { currentResume, setCurrentResume, resetGuided } = useResumeStore();
  const [isLoading, setIsLoading] = useState(true);
  const [title, setTitle] = useState("");
  const lastResumeId = useRef<string | null>(null);

  const fetchResume = useCallback(async () => {
    try {
      const { data } = await apiClient.get(API_ENDPOINTS.resumeDetail(resumeId));
      setCurrentResume(data);
      setTitle(data.title);
    } catch {
      router.push("/resumes");
    } finally {
      setIsLoading(false);
    }
  }, [resumeId, setCurrentResume, router]);

  useEffect(() => {
    if (lastResumeId.current !== resumeId) {
      // Only clear state when switching to a DIFFERENT resume
      setCurrentResume(null);
      resetGuided();
      lastResumeId.current = resumeId;
    }
    fetchResume();
  }, [fetchResume, resumeId, setCurrentResume, resetGuided]);

  const handleTitleSave = async () => {
    if (!currentResume || !title.trim()) return;
    try {
      const { data } = await apiClient.put(API_ENDPOINTS.resumeDetail(resumeId), { title });
      setCurrentResume({ ...currentResume, ...data });
    } catch { /* ignore */ }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!currentResume) return null;

  return (
    <div className="space-y-4 h-[calc(100vh-5rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-4 flex-shrink-0">
        <Button variant="ghost" size="icon" onClick={() => router.push("/resumes")}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex flex-1 items-center gap-2">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onBlur={handleTitleSave}
            className="max-w-xs text-lg font-semibold"
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3 flex-1 min-h-0">
        {/* Left: Guided AI Chat (2/3) */}
        <div className="lg:col-span-2 min-h-0">
          <GuidedResumeChat resumeId={resumeId} />
        </div>

        {/* Right: Resume Preview (1/3) */}
        <div className="min-h-0 overflow-hidden">
          <ResumePreview resumeId={resumeId} />
        </div>
      </div>
    </div>
  );
}
