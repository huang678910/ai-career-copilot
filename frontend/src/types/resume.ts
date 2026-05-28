export interface BasicInfo {
  name: string;
  phone: string;
  email: string;
  address: string;
  website: string;
  linkedin: string;
}

export interface ResumeEducation {
  id: string;
  resume_id: string;
  school: string;
  degree: string | null;
  major: string;
  start_date: string | null;
  end_date: string | null;
  gpa: string | null;
  description: string | null;
}

export interface ResumeWorkExperience {
  id: string;
  resume_id: string;
  company: string;
  title: string;
  location: string | null;
  start_date: string | null;
  end_date: string | null;
  current: boolean;
  description: string | null;
}

export interface ResumeProject {
  id: string;
  resume_id: string;
  name: string;
  role: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
  highlights: string[] | null;
  tech_stack: string[] | null;
  project_url: string | null;
}

export interface ResumeSkill {
  id: string;
  resume_id: string;
  category: string | null;
  name: string;
  level: string | null;
}

export interface Resume {
  id: string;
  user_id: string;
  title: string;
  basic_info: BasicInfo | null;
  summary: string | null;
  target_position: string | null;
  language: string;
  created_at: string;
  updated_at: string;
}

export interface ResumeDetail extends Resume {
  education: ResumeEducation[];
  work_experiences: ResumeWorkExperience[];
  projects: ResumeProject[];
  skills: ResumeSkill[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  timestamp: number;
}

export interface EducationInput {
  school: string;
  degree?: string;
  major: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  description?: string;
}

export interface WorkExperienceInput {
  company: string;
  title: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  current?: boolean;
  description?: string;
}

export interface ProjectInput {
  name: string;
  role?: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  highlights?: string[];
  tech_stack?: string[];
  project_url?: string;
}

export interface SkillInput {
  category?: string;
  name: string;
  level?: string;
}
