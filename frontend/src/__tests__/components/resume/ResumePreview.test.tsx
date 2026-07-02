import { describe, it, expect, beforeEach } from "@jest/globals";
import { render, screen } from "@testing-library/react";
import React from "react";
import "@testing-library/jest-dom";
import { useResumeStore } from "@/stores/resume-store";
import { ResumePreview } from "@/components/resume/ResumePreview";

const defaultState = {
  currentResume: null,
  chatMessages: [],
  isStreaming: false,
  guided: {
    currentSection: "",
    completedSections: [],
    collectedData: {},
    isReady: false,
  },
};

describe("ResumePreview", () => {
  beforeEach(() => {
    useResumeStore.setState(defaultState);
  });

  it("shows empty state when no data", () => {
    render(<ResumePreview resumeId="test-id" />);
    expect(screen.getByText("开始与 AI 对话后")).toBeInTheDocument();
  });

  it("shows basic info when provided via collectedData", () => {
    useResumeStore.setState({
      ...defaultState,
      guided: {
        ...defaultState.guided,
        collectedData: {
          basic_info: { name: "张三", email: "zhang@test.com", phone: "13800138000" },
        },
      },
    });
    render(<ResumePreview resumeId="test-id" />);
    expect(screen.getByText("张三")).toBeInTheDocument();
    expect(screen.getByText("zhang@test.com")).toBeInTheDocument();
  });

  it("shows education section", () => {
    useResumeStore.setState({
      ...defaultState,
      guided: {
        ...defaultState.guided,
        collectedData: {
          education: [
            { school: "清华大学", degree: "本科", major: "计算机科学", start_date: "2015-09", end_date: "2019-07" },
          ],
        },
      },
    });
    render(<ResumePreview resumeId="test-id" />);
    expect(screen.getByText("清华大学")).toBeInTheDocument();
  });

  it("shows skills section grouped by category", () => {
    useResumeStore.setState({
      ...defaultState,
      guided: {
        ...defaultState.guided,
        collectedData: {
          skills: [
            { category: "后端", name: "Python", level: "精通" },
            { category: "后端", name: "Go", level: "熟练" },
          ],
        },
      },
    });
    render(<ResumePreview resumeId="test-id" />);
    expect(screen.getByText(/Python \(精通\)/)).toBeInTheDocument();
  });

  it("shows work experience section", () => {
    useResumeStore.setState({
      ...defaultState,
      guided: {
        ...defaultState.guided,
        collectedData: {
          work_experience: [
            { company: "字节跳动", title: "高级工程师", start_date: "2020-03", end_date: "" },
          ],
        },
      },
    });
    render(<ResumePreview resumeId="test-id" />);
    expect(screen.getByText("字节跳动")).toBeInTheDocument();
  });

  it("shows summary section", () => {
    useResumeStore.setState({
      ...defaultState,
      guided: {
        ...defaultState.guided,
        collectedData: { summary: "5 years of experience." },
      },
    });
    render(<ResumePreview resumeId="test-id" />);
    expect(screen.getByText("5 years of experience.")).toBeInTheDocument();
  });

  it("shows AI generating indicator when isReady but no summary", () => {
    useResumeStore.setState({
      ...defaultState,
      guided: {
        ...defaultState.guided,
        isReady: true,
        collectedData: { basic_info: { name: "Test", email: "test@test.com" } },
      },
    });
    render(<ResumePreview resumeId="test-id" />);
    expect(screen.getByText("AI 正在生成专业总结...")).toBeInTheDocument();
  });

  it("renders all section headings for full data", () => {
    useResumeStore.setState({
      ...defaultState,
      guided: {
        ...defaultState.guided,
        collectedData: {
          basic_info: { name: "王五", email: "wang@test.com" },
          job_target: { target_position: "技术经理" },
          education: [{ school: "北京大学", degree: "硕士", major: "计算机", start_date: "2015-09", end_date: "2018-07" }],
          skills: [{ category: "后端", name: "Java", level: "熟练" }],
          projects: [{ name: "电商平台", role: "架构师", description: "高并发微服务架构" }],
          work_experience: [{ company: "阿里", title: "技术专家", start_date: "2018-08" }],
          summary: "10年技术经验。",
        },
      },
    });
    render(<ResumePreview resumeId="test-id" />);
    expect(screen.getByText("基本信息")).toBeInTheDocument();
    expect(screen.getByText("求职意向")).toBeInTheDocument();
    expect(screen.getByText("教育背景")).toBeInTheDocument();
    expect(screen.getByText("专业技能")).toBeInTheDocument();
    expect(screen.getByText("项目经历")).toBeInTheDocument();
    expect(screen.getByText("工作/实习经历")).toBeInTheDocument();
    expect(screen.getByText("自我评价")).toBeInTheDocument();
  });
});
