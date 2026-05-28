"use client";

import { useState } from "react";
import { Plus, Loader2, Pencil, X, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ResumeSection } from "./ResumeSection";
import { apiClient } from "@/lib/api-client";
import { API_ENDPOINTS } from "@/lib/api-endpoints";
import type { ResumeDetail } from "@/types/resume";

interface ResumeEditorProps {
  resume: ResumeDetail;
  onUpdate: (resume: ResumeDetail) => void;
}

export function ResumeEditor({ resume, onUpdate }: ResumeEditorProps) {
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Form states for each section
  const [summary, setSummary] = useState(resume.summary || "");
  const [targetPosition, setTargetPosition] = useState(resume.target_position || "");

  const showError = (err: any, fallback: string) => {
    const msg = err?.response?.data?.error?.message || err?.response?.data?.detail || err?.message || fallback;
    setError(msg);
    setTimeout(() => setError(""), 4000);
  };

  const showSuccess = (msg: string) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(""), 2000);
  };

  const handleSaveSummary = async () => {
    setSaving("summary");
    setError("");
    try {
      const { data } = await apiClient.put(API_ENDPOINTS.resumeDetail(resume.id), {
        summary,
        target_position: targetPosition,
      });
      onUpdate({ ...resume, ...data });
      showSuccess("保存成功");
    } catch (err: any) { showError(err, "保存失败"); }
    finally { setSaving(null); }
  };

  // --- Education ---
  const handleAddEducation = async () => {
    setSaving("edu-add");
    try {
      const { data } = await apiClient.post(API_ENDPOINTS.resumeEducation(resume.id), {
        school: "学校名称", major: "专业名称", degree: "本科",
      });
      onUpdate({ ...resume, education: [...resume.education, data] });
      showSuccess("添加成功");
    } catch (err: any) { showError(err, "添加失败"); }
    finally { setSaving(null); }
  };

  const handleUpdateEducation = async (eduId: string, fields: Record<string, any>) => {
    setSaving(eduId);
    setError("");
    try {
      const { data } = await apiClient.put(
        API_ENDPOINTS.resumeEducationItem(resume.id, eduId), fields
      );
      onUpdate({
        ...resume,
        education: resume.education.map((e) => (e.id === eduId ? data : e)),
      });
      showSuccess("更新成功");
    } catch (err: any) { showError(err, "更新失败"); }
    finally { setSaving(null); }
  };

  const handleDeleteEducation = async (eduId: string) => {
    try { await apiClient.delete(API_ENDPOINTS.resumeEducationItem(resume.id, eduId));
      onUpdate({ ...resume, education: resume.education.filter((e) => e.id !== eduId) });
      showSuccess("删除成功");
    } catch (err: any) { showError(err, "删除失败"); }
  };

  // --- Work Experience ---
  const handleAddExperience = async () => {
    setSaving("exp-add");
    try {
      const { data } = await apiClient.post(API_ENDPOINTS.resumeExperience(resume.id), {
        company: "公司名称", title: "职位名称",
      });
      onUpdate({ ...resume, work_experiences: [...resume.work_experiences, data] });
      showSuccess("添加成功");
    } catch (err: any) { showError(err, "添加失败"); }
    finally { setSaving(null); }
  };

  const handleUpdateExperience = async (expId: string, fields: Record<string, any>) => {
    setSaving(expId);
    setError("");
    try {
      const { data } = await apiClient.put(
        API_ENDPOINTS.resumeExperienceItem(resume.id, expId), fields
      );
      onUpdate({
        ...resume,
        work_experiences: resume.work_experiences.map((e) => (e.id === expId ? data : e)),
      });
      showSuccess("更新成功");
    } catch (err: any) { showError(err, "更新失败"); }
    finally { setSaving(null); }
  };

  const handleDeleteExperience = async (expId: string) => {
    try { await apiClient.delete(API_ENDPOINTS.resumeExperienceItem(resume.id, expId));
      onUpdate({ ...resume, work_experiences: resume.work_experiences.filter((e) => e.id !== expId) });
      showSuccess("删除成功");
    } catch (err: any) { showError(err, "删除失败"); }
  };

  // --- Projects ---
  const handleAddProject = async () => {
    setSaving("proj-add");
    try {
      const { data } = await apiClient.post(API_ENDPOINTS.resumeProjects(resume.id), {
        name: "项目名称", role: "角色",
      });
      onUpdate({ ...resume, projects: [...resume.projects, data] });
      showSuccess("添加成功");
    } catch (err: any) { showError(err, "添加失败"); }
    finally { setSaving(null); }
  };

  const handleUpdateProject = async (projId: string, fields: Record<string, any>) => {
    setSaving(projId);
    setError("");
    try {
      const { data } = await apiClient.put(
        API_ENDPOINTS.resumeProjectItem(resume.id, projId), fields
      );
      onUpdate({
        ...resume,
        projects: resume.projects.map((p) => (p.id === projId ? data : p)),
      });
      showSuccess("更新成功");
    } catch (err: any) { showError(err, "更新失败"); }
    finally { setSaving(null); }
  };

  const handleDeleteProject = async (projId: string) => {
    try { await apiClient.delete(API_ENDPOINTS.resumeProjectItem(resume.id, projId));
      onUpdate({ ...resume, projects: resume.projects.filter((p) => p.id !== projId) });
      showSuccess("删除成功");
    } catch (err: any) { showError(err, "删除失败"); }
  };

  // --- Skills ---
  const handleAddSkill = async () => {
    setSaving("skill-add");
    try {
      const { data } = await apiClient.post(API_ENDPOINTS.resumeSkills(resume.id), {
        name: "新技能", category: "其他",
      });
      onUpdate({ ...resume, skills: [...resume.skills, data] });
      showSuccess("添加成功");
    } catch (err: any) { showError(err, "添加失败"); }
    finally { setSaving(null); }
  };

  const handleUpdateSkill = async (skillId: string, fields: Record<string, any>) => {
    setSaving(skillId);
    setError("");
    try {
      const { data } = await apiClient.put(
        API_ENDPOINTS.resumeSkillItem(resume.id, skillId), fields
      );
      onUpdate({
        ...resume,
        skills: resume.skills.map((s) => (s.id === skillId ? data : s)),
      });
      showSuccess("更新成功");
    } catch (err: any) { showError(err, "更新失败"); }
    finally { setSaving(null); }
  };

  const handleDeleteSkill = async (skillId: string) => {
    try { await apiClient.delete(API_ENDPOINTS.resumeSkillItem(resume.id, skillId));
      onUpdate({ ...resume, skills: resume.skills.filter((s) => s.id !== skillId) });
      showSuccess("删除成功");
    } catch (err: any) { showError(err, "删除失败"); }
  };

  // --- Inline entity editor ---
  function EntityEditor({
    id, label, value, onChange,
  }: { id: string; label: string; value: string; onChange: (v: string) => void }) {
    return (
      <div className="mb-1">
        <label className="text-xs text-muted-foreground block mb-0.5">{label}</label>
        <Input value={value} onChange={(e) => onChange(e.target.value)} className="h-8 text-sm" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive">{error}</div>
      )}
      {successMsg && (
        <div className="rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-sm text-emerald-700 dark:bg-emerald-950 dark:border-emerald-800 dark:text-emerald-300">{successMsg}</div>
      )}

      {/* Summary + Target Position */}
      <ResumeSection title="基本信息">
        <div className="space-y-2">
          <div className="flex gap-2">
            <Input
              value={targetPosition}
              onChange={(e) => setTargetPosition(e.target.value)}
              placeholder="目标职位"
              className="h-9 text-sm flex-1"
            />
          </div>
          <Textarea value={summary} onChange={(e) => setSummary(e.target.value)} placeholder="个人总结..." rows={4} />
          <Button size="sm" onClick={handleSaveSummary} disabled={saving === "summary"}>
            {saving === "summary" && <Loader2 className="mr-1 h-3.5 w-3.5 animate-spin" />}
            <Save className="mr-1 h-3.5 w-3.5" />保存基本信息
          </Button>
        </div>
      </ResumeSection>

      {/* Education */}
      <ResumeSection title="教育经历">
        <div className="space-y-3">
          {resume.education.map((edu) => (
            <EditableEducation
              key={edu.id}
              edu={edu}
              resumeId={resume.id}
              saving={saving}
              onSave={handleUpdateEducation}
              onDelete={handleDeleteEducation}
            />
          ))}
          <Button variant="outline" size="sm" onClick={handleAddEducation} disabled={saving === "edu-add"}>
            <Plus className="mr-1 h-3.5 w-3.5" /> 添加教育经历
          </Button>
        </div>
      </ResumeSection>

      {/* Work Experience */}
      <ResumeSection title="工作经历">
        <div className="space-y-3">
          {resume.work_experiences.map((exp) => (
            <EditableWorkExperience
              key={exp.id}
              exp={exp}
              resumeId={resume.id}
              saving={saving}
              onSave={handleUpdateExperience}
              onDelete={handleDeleteExperience}
            />
          ))}
          <Button variant="outline" size="sm" onClick={handleAddExperience} disabled={saving === "exp-add"}>
            <Plus className="mr-1 h-3.5 w-3.5" /> 添加工作经历
          </Button>
        </div>
      </ResumeSection>

      {/* Projects */}
      <ResumeSection title="项目经验">
        <div className="space-y-3">
          {resume.projects.map((proj) => (
            <EditableProject
              key={proj.id}
              proj={proj}
              resumeId={resume.id}
              saving={saving}
              onSave={handleUpdateProject}
              onDelete={handleDeleteProject}
            />
          ))}
          <Button variant="outline" size="sm" onClick={handleAddProject} disabled={saving === "proj-add"}>
            <Plus className="mr-1 h-3.5 w-3.5" /> 添加项目
          </Button>
        </div>
      </ResumeSection>

      {/* Skills */}
      <ResumeSection title="技能栈">
        <div className="space-y-2">
          <div className="flex flex-wrap gap-2">
            {resume.skills.map((skill) => (
              <EditableSkill
                key={skill.id}
                skill={skill}
                resumeId={resume.id}
                saving={saving}
                onSave={handleUpdateSkill}
                onDelete={handleDeleteSkill}
              />
            ))}
          </div>
          <Button variant="outline" size="sm" onClick={handleAddSkill} disabled={saving === "skill-add"}>
            <Plus className="mr-1 h-3.5 w-3.5" /> 添加技能
          </Button>
        </div>
      </ResumeSection>
    </div>
  );
}

// --- Inline editable sub-components ---

function EditableEducation({ edu, resumeId, saving, onSave, onDelete }: any) {
  const [edit, setEdit] = useState(false);
  const [school, setSchool] = useState(edu.school);
  const [major, setMajor] = useState(edu.major || "");
  const [degree, setDegree] = useState(edu.degree || "");
  const [desc, setDesc] = useState(edu.description || "");

  if (!edit) {
    return (
      <div className="flex items-start justify-between rounded border p-3 text-sm">
        <div>
          <span className="font-medium">{edu.school}</span>
          <span className="text-muted-foreground ml-2">{edu.major} · {edu.degree || "本科"}</span>
          {edu.description && <p className="text-xs text-muted-foreground mt-1">{edu.description}</p>}
        </div>
        <div className="flex gap-1 shrink-0 ml-2">
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setEdit(true)}>
            <Pencil className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onDelete(edu.id)}>
            <X className="h-3.5 w-3.5 text-destructive" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded border p-3 space-y-2 text-sm">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-xs text-muted-foreground">学校</label>
          <Input value={school} onChange={(e) => setSchool(e.target.value)} className="h-8 text-sm" />
        </div>
        <div>
          <label className="text-xs text-muted-foreground">专业</label>
          <Input value={major} onChange={(e) => setMajor(e.target.value)} className="h-8 text-sm" />
        </div>
        <div>
          <label className="text-xs text-muted-foreground">学位</label>
          <Input value={degree} onChange={(e) => setDegree(e.target.value)} className="h-8 text-sm" placeholder="本科/硕士/博士" />
        </div>
        <div>
          <label className="text-xs text-muted-foreground">描述</label>
          <Input value={desc} onChange={(e) => setDesc(e.target.value)} className="h-8 text-sm" placeholder="简要描述" />
        </div>
      </div>
      <div className="flex gap-2">
        <Button size="sm" disabled={saving === edu.id} onClick={() => onSave(edu.id, { school, major, degree, description: desc })}>
          {saving === edu.id && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}保存
        </Button>
        <Button size="sm" variant="outline" onClick={() => setEdit(false)}>取消</Button>
      </div>
    </div>
  );
}

function EditableWorkExperience({ exp, resumeId, saving, onSave, onDelete }: any) {
  const [edit, setEdit] = useState(false);
  const [company, setCompany] = useState(exp.company);
  const [title, setTitle] = useState(exp.title || "");
  const [location, setLocation] = useState(exp.location || "");
  const [desc, setDesc] = useState(exp.description || "");

  if (!edit) {
    return (
      <div className="flex items-start justify-between rounded border p-3 text-sm">
        <div>
          <span className="font-medium">{exp.company}</span>
          <span className="text-muted-foreground ml-2">{exp.title}</span>
          {exp.location && <span className="text-muted-foreground ml-1">· {exp.location}</span>}
          {exp.description && <p className="text-xs text-muted-foreground mt-1">{exp.description}</p>}
        </div>
        <div className="flex gap-1 shrink-0 ml-2">
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setEdit(true)}>
            <Pencil className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onDelete(exp.id)}>
            <X className="h-3.5 w-3.5 text-destructive" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded border p-3 space-y-2 text-sm">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-xs text-muted-foreground">公司</label>
          <Input value={company} onChange={(e) => setCompany(e.target.value)} className="h-8 text-sm" />
        </div>
        <div>
          <label className="text-xs text-muted-foreground">职位</label>
          <Input value={title} onChange={(e) => setTitle(e.target.value)} className="h-8 text-sm" />
        </div>
        <div>
          <label className="text-xs text-muted-foreground">地点</label>
          <Input value={location} onChange={(e) => setLocation(e.target.value)} className="h-8 text-sm" />
        </div>
        <div>
          <label className="text-xs text-muted-foreground">描述</label>
          <Input value={desc} onChange={(e) => setDesc(e.target.value)} className="h-8 text-sm" placeholder="工作内容描述" />
        </div>
      </div>
      <div className="flex gap-2">
        <Button size="sm" disabled={saving === exp.id} onClick={() => onSave(exp.id, { company, title, location, description: desc })}>
          {saving === exp.id && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}保存
        </Button>
        <Button size="sm" variant="outline" onClick={() => setEdit(false)}>取消</Button>
      </div>
    </div>
  );
}

function EditableProject({ proj, resumeId, saving, onSave, onDelete }: any) {
  const [edit, setEdit] = useState(false);
  const [name, setName] = useState(proj.name);
  const [role, setRole] = useState(proj.role || "");
  const [desc, setDesc] = useState(proj.description || "");
  const [techStack, setTechStack] = useState((proj.tech_stack || []).join(", "));

  if (!edit) {
    return (
      <div className="flex items-start justify-between rounded border p-3 text-sm">
        <div>
          <span className="font-medium">{proj.name}</span>
          {proj.role && <span className="text-muted-foreground ml-2">· {proj.role}</span>}
          {proj.description && <p className="text-xs text-muted-foreground mt-1">{proj.description}</p>}
          {proj.tech_stack && proj.tech_stack.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {proj.tech_stack.map((t: string) => <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>)}
            </div>
          )}
        </div>
        <div className="flex gap-1 shrink-0 ml-2">
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setEdit(true)}>
            <Pencil className="h-3.5 w-3.5" />
          </Button>
          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => onDelete(proj.id)}>
            <X className="h-3.5 w-3.5 text-destructive" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded border p-3 space-y-2 text-sm">
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-xs text-muted-foreground">项目名称</label>
          <Input value={name} onChange={(e) => setName(e.target.value)} className="h-8 text-sm" />
        </div>
        <div>
          <label className="text-xs text-muted-foreground">角色</label>
          <Input value={role} onChange={(e) => setRole(e.target.value)} className="h-8 text-sm" />
        </div>
        <div className="col-span-2">
          <label className="text-xs text-muted-foreground">描述</label>
          <Textarea value={desc} onChange={(e) => setDesc(e.target.value)} className="text-sm" rows={3} />
        </div>
        <div className="col-span-2">
          <label className="text-xs text-muted-foreground">技术栈（逗号分隔）</label>
          <Input value={techStack} onChange={(e) => setTechStack(e.target.value)} className="h-8 text-sm" />
        </div>
      </div>
      <div className="flex gap-2">
        <Button size="sm" disabled={saving === proj.id} onClick={() => onSave(proj.id, {
          name, role, description: desc,
          tech_stack: techStack.split(",").map((s: string) => s.trim()).filter(Boolean),
        })}>
          {saving === proj.id && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}保存
        </Button>
        <Button size="sm" variant="outline" onClick={() => setEdit(false)}>取消</Button>
      </div>
    </div>
  );
}

function EditableSkill({ skill, resumeId, saving, onSave, onDelete }: any) {
  const [edit, setEdit] = useState(false);
  const [name, setName] = useState(skill.name);
  const [category, setCategory] = useState(skill.category || "其他");
  const [level, setLevel] = useState(skill.level || "");

  if (!edit) {
    return (
      <div className="group relative inline-flex">
        <Badge variant="outline" className="pr-7 cursor-pointer" onClick={() => setEdit(true)}>
          {skill.name}
          <span className="ml-1 text-xs text-muted-foreground">{skill.level}</span>
        </Badge>
        <button className="absolute right-0.5 top-0.5 text-muted-foreground hover:text-destructive" onClick={(e) => { e.stopPropagation(); onDelete(skill.id); }}>
          <X className="h-3 w-3" />
        </button>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-1 rounded border p-2 text-sm">
      <Input value={name} onChange={(e) => setName(e.target.value)} className="h-7 w-24 text-sm" placeholder="技能" />
      <Input value={category} onChange={(e) => setCategory(e.target.value)} className="h-7 w-20 text-sm" placeholder="分类" />
      <select value={level} onChange={(e) => setLevel(e.target.value)} className="h-7 rounded border bg-background text-xs">
        <option value="">级别</option>
        <option value="入门">入门</option>
        <option value="熟练">熟练</option>
        <option value="精通">精通</option>
        <option value="专家">专家</option>
      </select>
      <Button size="sm" variant="ghost" className="h-7 px-2 text-xs" disabled={saving === skill.id}
        onClick={() => onSave(skill.id, { name, category, level })}>
        {saving === skill.id && <Loader2 className="mr-1 h-3 w-3 animate-spin" />}保存
      </Button>
      <Button size="sm" variant="ghost" className="h-7 px-1" onClick={() => setEdit(false)}>
        <X className="h-3.5 w-3.5" />
      </Button>
    </div>
  );
}
