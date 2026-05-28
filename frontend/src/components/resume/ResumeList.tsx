"use client";

import Link from "next/link";
import { FileText, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import type { Resume } from "@/types/resume";

interface ResumeListProps {
  resumes: Resume[];
  isLoading: boolean;
  onCreate: () => void;
  onDelete: (id: string) => void;
}

export function ResumeList({ resumes, isLoading, onCreate, onDelete }: ResumeListProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {resumes.map((resume) => (
        <div key={resume.id} className="relative group">
          <Link href={`/resumes/${resume.id}`}>
            <Card className="h-full transition-shadow hover:shadow-md cursor-pointer">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{resume.title}</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </div>
                <CardDescription>
                  {resume.target_position || "未设定目标职位"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Badge variant="secondary">{resume.language === "zh" ? "中文" : "English"}</Badge>
                  <span>更新于 {new Date(resume.updated_at).toLocaleDateString("zh-CN")}</span>
                </div>
                {resume.summary && (
                  <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                    {resume.summary}
                  </p>
                )}
              </CardContent>
            </Card>
          </Link>
          <button
            onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDelete(resume.id); }}
            className="absolute top-2 right-2 h-8 w-8 rounded-md bg-destructive/10 text-destructive opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center hover:bg-destructive/20"
            title="删除简历"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      ))}

      <button
        onClick={onCreate}
        className="flex h-full min-h-[180px] flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-muted-foreground/25 p-6 text-muted-foreground transition-colors hover:border-primary/50 hover:text-primary"
      >
        <Plus className="h-8 w-8" />
        <span className="text-sm font-medium">创建新简历</span>
      </button>
    </div>
  );
}
