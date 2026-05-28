"use client";

import { useState, useRef } from "react";
import { Upload, Loader2, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";
import { useRouter } from "next/navigation";

interface ResumeUploadProps {
  onClose: () => void;
}

export function ResumeUpload({ onClose }: ResumeUploadProps) {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File | null) => {
    if (!f) return;
    const allowed = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"];
    if (!allowed.includes(f.type)) {
      setError("仅支持 PDF、DOCX 和 TXT 文件");
      return;
    }
    setFile(f);
    setError("");
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const form = new FormData();
      form.append("file", file);
      const { data } = await apiClient.post("/api/v1/resumes/import", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      router.push(`/resumes/${data.id}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "导入失败，请重试");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="w-full max-w-md rounded-xl bg-background p-6 shadow-lg" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-bold mb-2">导入简历</h2>
        <p className="text-sm text-muted-foreground mb-4">上传 PDF、DOCX 或 TXT 文件，AI 将自动提取结构化信息</p>

        <div
          className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 mb-4 transition-colors cursor-pointer
            ${dragOver ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
          onClick={() => inputRef.current?.click()}
        >
          <input ref={inputRef} type="file" className="hidden" accept=".pdf,.docx,.doc,.txt" onChange={(e) => handleFile(e.target.files?.[0] || null)} />
          {file ? (
            <div className="flex flex-col items-center gap-2">
              <FileText className="h-10 w-10 text-primary" />
              <span className="text-sm font-medium">{file.name}</span>
              <span className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</span>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 text-muted-foreground">
              <Upload className="h-10 w-10" />
              <span className="text-sm">点击或拖拽文件到此处</span>
              <span className="text-xs">支持 PDF、DOCX、TXT</span>
            </div>
          )}
        </div>

        {error && <p className="text-sm text-destructive mb-4">{error}</p>}

        <div className="flex gap-2 justify-end">
          <Button variant="outline" onClick={onClose}>取消</Button>
          <Button onClick={handleUpload} disabled={!file || uploading}>
            {uploading && <Loader2 className="mr-1 h-4 w-4 animate-spin" />}
            {uploading ? "AI 解析中..." : "开始导入"}
          </Button>
        </div>
      </div>
    </div>
  );
}
