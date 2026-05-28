export const API_ENDPOINTS = {
  auth: {
    register: "/api/v1/auth/register",
    login: "/api/v1/auth/login",
    refresh: "/api/v1/auth/refresh",
    logout: "/api/v1/auth/logout",
    me: "/api/v1/auth/me",
  },
  resumes: "/api/v1/resumes",
  resumeDetail: (resumeId: string) => `/api/v1/resumes/${resumeId}`,
  resumeEducation: (resumeId: string) => `/api/v1/resumes/${resumeId}/education`,
  resumeEducationItem: (resumeId: string, eduId: string) =>
    `/api/v1/resumes/${resumeId}/education/${eduId}`,
  resumeExperience: (resumeId: string) => `/api/v1/resumes/${resumeId}/experience`,
  resumeExperienceItem: (resumeId: string, expId: string) =>
    `/api/v1/resumes/${resumeId}/experience/${expId}`,
  resumeProjects: (resumeId: string) => `/api/v1/resumes/${resumeId}/projects`,
  resumeProjectItem: (resumeId: string, projId: string) =>
    `/api/v1/resumes/${resumeId}/projects/${projId}`,
  resumeSkills: (resumeId: string) => `/api/v1/resumes/${resumeId}/skills`,
  resumeSkillItem: (resumeId: string, skillId: string) =>
    `/api/v1/resumes/${resumeId}/skills/${skillId}`,
  jobs: "/api/v1/jobs",
  jdAnalysis: "/api/v1/jd-analysis",
  tailor: "/api/v1/tailor",
  interviewQuestions: "/api/v1/interview/questions",
  interviewSessions: "/api/v1/interview/sessions",
  export: "/api/v1/export",
} as const;
