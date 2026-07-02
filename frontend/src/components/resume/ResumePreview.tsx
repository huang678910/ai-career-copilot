"use client";

import { useState } from "react";
import { FileDown, FileText, Eye, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useResumeStore } from "@/stores/resume-store";
import { apiClient } from "@/lib/api-client";

const SECTION_LABELS: Record<string, string> = {
  basic_info: "基本信息",
  job_target: "求职意向",
  education: "教育背景",
  skills: "专业技能",
  projects: "项目经历",
  work_experience: "工作/实习经历",
};

const TEMPLATE_STYLES: Record<string, { fontFamily: string; primaryColor: string; bgHeader: string; sectionStyle: "underline" | "bold-line" | "minimal" }> = {
  professional: {
    fontFamily: "'Microsoft YaHei', 'PingFang SC', sans-serif",
    primaryColor: "#1a1a1a",
    bgHeader: "transparent",
    sectionStyle: "bold-line",
  },
  modern: {
    fontFamily: "'Microsoft YaHei', 'PingFang SC', sans-serif",
    primaryColor: "#2563eb",
    bgHeader: "#f8fafc",
    sectionStyle: "underline",
  },
  classic: {
    fontFamily: "'SimSun', 'STSong', 'Noto Serif SC', serif",
    primaryColor: "#1a1a1a",
    bgHeader: "transparent",
    sectionStyle: "bold-line",
  },
  compact: {
    fontFamily: "'Microsoft YaHei', 'PingFang SC', sans-serif",
    primaryColor: "#374151",
    bgHeader: "transparent",
    sectionStyle: "minimal",
  },
};

interface Props {
  resumeId: string;
}

export function ResumePreview({ resumeId }: Props) {
  const { guided, currentResume } = useResumeStore();
  const { collectedData, isReady } = guided;
  const [exporting, setExporting] = useState<"pdf" | "docx" | null>(null);
  const [template, setTemplate] = useState("professional");

  const ts = TEMPLATE_STYLES[template] || TEMPLATE_STYLES.modern;

  const sectionTitleStyle = (): React.CSSProperties => ({
    color: ts.primaryColor,
    borderBottom: ts.sectionStyle === "underline" ? `2px solid ${ts.primaryColor}` :
                   ts.sectionStyle === "bold-line" ? "1px solid #ddd" : "none",
    paddingBottom: 3,
    fontWeight: 700,
    fontSize: 12,
    marginBottom: 6,
  });

  // Build display data with MERGE strategy:
  // Start from DB currentResume, then overlay persisted guided_data,
  // then overlay live collectedData — each layer only overrides
  // sections that have actual data, never blanks out filled sections.
  const displayData = (() => {
    const r = currentResume as any;
    const base: Record<string, any> = {};

    // Layer 1: Build from currentResume DB fields
    if (r) {
      const info = r.basic_info || {};
      if (info.name || info.email || info.phone) base.basic_info = info;
      if (r.target_position) base.job_target = { ...base.job_target, target_position: r.target_position };
      if (r.education?.length) base.education = r.education;
      if (r.skills?.length) base.skills = r.skills;
      if (r.projects?.length) base.projects = r.projects;
      if (r.work_experiences?.length) base.work_experience = r.work_experiences;
      if (r.summary) base.summary = r.summary;
    }

    // Layer 2: Overlay persisted guided_data (from previous AI session)
    if (r?.guided_data && typeof r.guided_data === "object") {
      for (const key of Object.keys(r.guided_data)) {
        if (key === "_meta") continue;
        const val = r.guided_data[key];
        if (val && (typeof val !== "object" || Object.keys(val).length > 0)) {
          base[key] = val;
        }
      }
    }

    // Layer 3: Overlay live collectedData (from WebSocket) — only non-empty sections
    if (collectedData && typeof collectedData === "object") {
      for (const key of Object.keys(collectedData)) {
        if (key === "_meta") continue;
        const val = collectedData[key];
        if (Array.isArray(val) && val.length > 0) base[key] = val;
        else if (val && typeof val === "object" && Object.keys(val).length > 0) base[key] = val;
        else if (typeof val === "string" && val.length > 0) base[key] = val;
      }
      // Preserve summary from collectedData even if empty (user may have cleared it)
      if ("summary" in collectedData && collectedData.summary) base.summary = collectedData.summary;
    }

    return base;
  })();

  const sections = Object.entries(displayData).filter(
    ([key]) => key !== "summary"
  );

  const handleExport = async (format: "pdf" | "docx") => {
    setExporting(format);
    try {
      const endpoint = `/api/v1/export/resume/${resumeId}/${format}/sync`;
      const res = await apiClient.post(
        endpoint,
        // Send the structured resume data for export — not chat messages
        { resume_data: collectedData, template },
        { responseType: "blob", timeout: 30000 }
      );
      const blob = new Blob([res.data]);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `resume_${resumeId}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("导出失败，请重试");
    } finally {
      setExporting(null);
    }
  };

  const renderBasicInfo = (data: Record<string, any>) => (
    <div className="mb-3">
      {data.name && <p className="font-bold text-base mb-1">{data.name}</p>}
      <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-[11px] text-muted-foreground">
        {data.email && <span>{data.email}</span>}
        {data.phone && <span>{data.phone}</span>}
        {data.city && <span>{data.city}</span>}
      </div>
    </div>
  );

  const renderJobTarget = (data: Record<string, any>) => (
    <p className="text-[11px] mb-2" style={{ color: ts.primaryColor }}>
      求职意向：{data.target_position || "未设置"}
      {data.industry && ` · ${data.industry}`}
      {data.city && ` · ${data.city}`}
      {data.salary && ` · ${data.salary}`}
    </p>
  );

  const renderEducation = (data: any[]) => {
    if (!Array.isArray(data)) return null;
    return (
      <div className="space-y-1.5">
        {data.map((edu, i) => (
          <div key={i} className="text-[11px] leading-relaxed">
            <span className="font-medium">{edu.school}</span>
            <span className="text-muted-foreground"> · {edu.degree} · {edu.major}</span>
            <span className="float-right text-muted-foreground">{edu.start_date} - {edu.end_date}</span>
            {edu.gpa && <span className="text-muted-foreground"> · GPA {edu.gpa}</span>}
            {edu.description && <p className="text-muted-foreground mt-0.5">{edu.description}</p>}
          </div>
        ))}
      </div>
    );
  };

  const renderSkills = (data: any[]) => {
    if (!Array.isArray(data)) return null;
    const groups: Record<string, string[]> = {};
    for (const s of data) {
      const cat = s.category || "其他";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(s.name + (s.level ? ` (${s.level})` : ""));
    }
    return (
      <div className="space-y-1 text-[11px]">
        {Object.entries(groups).map(([cat, names]) => (
          <p key={cat} className="leading-relaxed">
            <span className="font-medium">{cat}：</span>
            <span className="text-muted-foreground">{names.join("、")}</span>
          </p>
        ))}
      </div>
    );
  };

  const renderExperience = (data: any[], type: "projects" | "work_experience") => {
    if (!Array.isArray(data)) return null;
    return (
      <div className="space-y-2">
        {data.map((item, i) => (
          <div key={i} className="text-[11px] leading-relaxed">
            <div className="mb-0.5">
              <span className="font-medium">
                {type === "work_experience" ? item.company : item.name}
              </span>
              {type === "work_experience" && item.title && (
                <span className="text-muted-foreground"> · {item.title}</span>
              )}
              {type === "projects" && item.role && (
                <span className="text-muted-foreground"> · {item.role}</span>
              )}
              <span className="float-right text-muted-foreground">{item.start_date} - {item.end_date}</span>
            </div>
            {item.description && (
              <p className="text-muted-foreground">{item.description}</p>
            )}
            {item.highlights && Array.isArray(item.highlights) && (
              <ul className="list-disc list-inside text-muted-foreground pl-1">
                {item.highlights.map((h: string, j: number) => (
                  <li key={j}>{h}</li>
                ))}
              </ul>
            )}
            {item.tech_stack && Array.isArray(item.tech_stack) && (
              <p className="text-muted-foreground mt-0.5">
                <span className="font-medium">技术栈：</span>{item.tech_stack.join("、")}
              </p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const isEmpty = sections.length === 0 && !displayData.summary;

  return (
    <Card className="h-full flex flex-col" style={{ fontFamily: ts.fontFamily }}>
      <CardHeader className="flex-shrink-0" style={{ background: ts.bgHeader }}>
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">简历预览</CardTitle>
          <div className="flex items-center gap-1">
            <select
              className="text-xs border rounded px-1.5 py-1"
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
            >
              <option value="professional">专业模板</option>
              <option value="modern">现代风格</option>
              <option value="classic">经典风格</option>
            </select>
            <Button
              variant="outline" size="sm"
              disabled={exporting !== null}
              onClick={() => handleExport("pdf")}
            >
              {exporting === "pdf" ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FileDown className="h-3.5 w-3.5" />}
              <span className="ml-1 text-xs">PDF</span>
            </Button>
            <Button
              variant="outline" size="sm"
              disabled={exporting !== null}
              onClick={() => handleExport("docx")}
            >
              {exporting === "docx" ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FileText className="h-3.5 w-3.5" />}
              <span className="ml-1 text-xs">DOCX</span>
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto" style={{ padding: "12px 16px" }}>
        {isEmpty ? (
          <div className="flex items-center justify-center min-h-[300px] text-center">
            <div className="space-y-2 text-muted-foreground">
              <Eye className="h-8 w-8 mx-auto" />
              <p className="text-sm">开始与 AI 对话后</p>
              <p className="text-xs">简历信息将在此实时显示</p>
            </div>
          </div>
        ) : (
          <div className="text-[11px] leading-relaxed space-y-3" style={{ fontFamily: ts.fontFamily }}>
            {sections.map(([key, data]) => (
          <div key={key}>
            <p style={sectionTitleStyle()}>
              {SECTION_LABELS[key] || key}
            </p>
            {key === "basic_info" && renderBasicInfo(data as Record<string, any>)}
            {key === "job_target" && renderJobTarget(data as Record<string, any>)}
            {key === "education" && renderEducation(data as any[])}
            {key === "skills" && renderSkills(data as any[])}
            {key === "projects" && renderExperience(data as any[], "projects")}
            {key === "work_experience" && renderExperience(data as any[], "work_experience")}
          </div>
        ))}

            {/* Summary — rendered at the bottom like 自我评价 */}
            {displayData.summary && (
              <div>
                <p style={sectionTitleStyle()}>自我评价</p>
                <p className="text-[11px] text-muted-foreground leading-relaxed">{displayData.summary}</p>
              </div>
            )}

            {isReady && !displayData.summary && (
              <div className="flex items-center gap-2 text-[11px] text-amber-600 bg-amber-50 rounded p-2 dark:bg-amber-950 dark:text-amber-400">
                <Loader2 className="h-3 w-3 animate-spin" />
                AI 正在生成专业总结...
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
