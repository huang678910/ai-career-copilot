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
  const [template, setTemplate] = useState("modern");

  const ts = TEMPLATE_STYLES[template] || TEMPLATE_STYLES.modern;

  const sectionTitleStyle = (): React.CSSProperties => ({
    color: ts.primaryColor,
    borderBottom: ts.sectionStyle === "underline" ? `2px solid ${ts.primaryColor}` :
                   ts.sectionStyle === "bold-line" ? "1px solid #999" : "none",
    paddingBottom: ts.sectionStyle === "minimal" ? 0 : 4,
    fontWeight: ts.sectionStyle === "minimal" ? 600 : 700,
    textTransform: ts.sectionStyle === "minimal" ? "uppercase" as const : "none",
    letterSpacing: ts.sectionStyle === "minimal" ? "1px" : "normal",
    fontSize: 11,
  });

  // Build display data: prefer guided collectedData, then DB guided_data, then currentResume fields
  const displayData = (() => {
    if (Object.keys(collectedData).length > 0) return collectedData;
    if (!currentResume) return {};
    // Check for persisted guided_data from previous AI conversation
    const r = currentResume as any;
    if (r.guided_data && Object.keys(r.guided_data).length > 0) {
      return r.guided_data;
    }
    // Fall back to building from currentResume fields
    const info = r.basic_info || {};
    const data: Record<string, any> = {};
    if (info.name || info.email || info.phone) {
      data.basic_info = info;
    }
    if (r.target_position) {
      data.job_target = { target_position: r.target_position };
    }
    if (r.education?.length) {
      data.education = r.education.map((e: any) => ({
        school: e.school, degree: e.degree, major: e.major,
        start_date: e.start_date, end_date: e.end_date, gpa: e.gpa,
      }));
    }
    if (r.skills?.length) {
      data.skills = r.skills.map((s: any) => ({
        category: s.category, name: s.name, level: s.level,
      }));
    }
    if (r.projects?.length) {
      data.projects = r.projects.map((p: any) => ({
        name: p.name, role: p.role, start_date: p.start_date, end_date: p.end_date,
        description: p.description, tech_stack: p.tech_stack, highlights: p.highlights,
      }));
    }
    if (r.work_experiences?.length) {
      data.work_experience = r.work_experiences.map((w: any) => ({
        company: w.company, title: w.title, location: w.location,
        start_date: w.start_date, end_date: w.end_date, description: w.description,
        highlights: w.highlights,
      }));
    }
    if (r.summary) {
      data.summary = r.summary;
    }
    return data;
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
    <div className="space-y-1">
      {data.name && <p className="font-bold text-lg">{data.name}</p>}
      <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-xs text-muted-foreground">
        {data.email && <span>{data.email}</span>}
        {data.phone && <span>{data.phone}</span>}
        {data.city && <span>{data.city}</span>}
      </div>
    </div>
  );

  const renderJobTarget = (data: Record<string, any>) => (
    <div className="flex items-center gap-2 flex-wrap">
      <Badge variant="secondary" className="text-xs" style={{ color: ts.primaryColor, borderColor: ts.primaryColor }}>
        {data.target_position || "未设置"}
      </Badge>
      {data.industry && <span className="text-xs text-muted-foreground">{data.industry}</span>}
      {data.city && <span className="text-xs text-muted-foreground">{data.city}</span>}
      {data.salary && <span className="text-xs text-muted-foreground">期望薪资：{data.salary}</span>}
    </div>
  );

  const renderEducation = (data: any[]) => {
    if (!Array.isArray(data)) return null;
    return (
      <div className="space-y-2">
        {data.map((edu, i) => (
          <div key={i} className="text-xs space-y-0.5">
            <div className="flex justify-between">
              <span className="font-medium">{edu.school}</span>
              <span className="text-muted-foreground">{edu.start_date} - {edu.end_date}</span>
            </div>
            <p className="text-muted-foreground">{edu.degree} · {edu.major}{edu.gpa ? ` · GPA ${edu.gpa}` : ""}</p>
            {edu.description && <p className="text-muted-foreground leading-relaxed">{edu.description}</p>}
          </div>
        ))}
      </div>
    );
  };

  const renderSkills = (data: any[]) => {
    if (!Array.isArray(data)) return null;
    // Group by category
    const groups: Record<string, string[]> = {};
    for (const s of data) {
      const cat = s.category || "其他";
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(s.name + (s.level ? ` (${s.level})` : ""));
    }
    return (
      <div className="flex flex-wrap gap-1.5">
        {Object.entries(groups).map(([cat, names]) => (
          <div key={cat} className="flex items-center gap-1">
            {names.map((name, i) => (
              <Badge key={i} variant="outline" className="text-[10px]">{name}</Badge>
            ))}
          </div>
        ))}
      </div>
    );
  };

  const renderExperience = (data: any[], type: "projects" | "work_experience") => {
    if (!Array.isArray(data)) return null;
    return (
      <div className="space-y-3">
        {data.map((item, i) => (
          <div key={i} className="text-xs space-y-1">
            <div className="flex justify-between">
              <span className="font-medium">
                {type === "work_experience" ? item.company : item.name}
              </span>
              <span className="text-muted-foreground">{item.start_date} - {item.end_date}</span>
            </div>
            <p className="text-muted-foreground font-medium">
              {type === "work_experience" ? item.title : item.role}
              {type === "work_experience" && item.location && <span className="font-normal"> ({item.location})</span>}
            </p>
            {item.description && (
              <p className="text-muted-foreground leading-relaxed">{item.description}</p>
            )}
            {item.highlights && Array.isArray(item.highlights) && (
              <ul className="list-disc list-inside text-muted-foreground space-y-0.5">
                {item.highlights.map((h: string, j: number) => (
                  <li key={j}>{h}</li>
                ))}
              </ul>
            )}
            {item.tech_stack && Array.isArray(item.tech_stack) && (
              <div className="flex gap-1 flex-wrap">
                {item.tech_stack.map((t: string, k: number) => (
                  <Badge key={k} variant="secondary" className="text-[10px]">{t}</Badge>
                ))}
              </div>
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
              <option value="modern">现代风格</option>
              <option value="classic">经典风格</option>
              <option value="compact">紧凑风格</option>
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
      <CardContent className="flex-1 overflow-y-auto space-y-4">
        {isEmpty ? (
          <div className="flex items-center justify-center min-h-[300px] text-center">
            <div className="space-y-2 text-muted-foreground">
              <Eye className="h-8 w-8 mx-auto" />
              <p className="text-sm">开始与 AI 对话后</p>
              <p className="text-xs">简历信息将在此实时显示</p>
            </div>
          </div>
        ) : (
          <>
            {/* Summary */}
            {displayData.summary && (
              <div className="p-3 rounded-lg border" style={{ background: `${ts.primaryColor}08`, borderColor: `${ts.primaryColor}18` }}>
                <p className="text-xs font-medium mb-1" style={{ color: ts.primaryColor }}>个人总结</p>
                <p className="text-xs text-muted-foreground leading-relaxed">{displayData.summary}</p>
              </div>
            )}

            {isReady && !displayData.summary && (
              <div className="flex items-center gap-2 text-xs text-amber-600 bg-amber-50 rounded-lg p-2 dark:bg-amber-950 dark:text-amber-400">
                <Loader2 className="h-3 w-3 animate-spin" />
                AI 正在生成专业总结...
              </div>
            )}

            {/* Sections */}
            {sections.map(([key, data]) => (
          <div key={key} className="space-y-1.5">
            <p className="text-[11px] tracking-wide" style={sectionTitleStyle()}>
              {SECTION_LABELS[key] || key}
            </p>
            <div className="pl-1">
              {key === "basic_info" && renderBasicInfo(data as Record<string, any>)}
              {key === "job_target" && renderJobTarget(data as Record<string, any>)}
              {key === "education" && renderEducation(data as any[])}
              {key === "skills" && renderSkills(data as any[])}
              {key === "projects" && renderExperience(data as any[], "projects")}
              {key === "work_experience" && renderExperience(data as any[], "work_experience")}
            </div>
          </div>
        ))}
          </>
        )}
      </CardContent>
    </Card>
  );
}
