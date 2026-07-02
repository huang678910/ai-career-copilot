import { describe, it, expect } from "@jest/globals";
import { render, screen } from "@testing-library/react";
import React from "react";
import "@testing-library/jest-dom";
import { ChatMessageBubble } from "@/components/resume/ChatMessage";

describe("ChatMessageBubble", () => {
  const aiMessage = {
    id: "1",
    role: "ai" as const,
    content: "Hello, I am AI.",
    timestamp: Date.now(),
  };

  const userMessage = {
    id: "2",
    role: "user" as const,
    content: "Hello, I am User.",
    timestamp: Date.now(),
  };

  it("renders AI message content", () => {
    render(<ChatMessageBubble message={aiMessage} />);
    expect(screen.getByText("Hello, I am AI.")).toBeInTheDocument();
  });

  it("renders user message content", () => {
    render(<ChatMessageBubble message={userMessage} />);
    expect(screen.getByText("Hello, I am User.")).toBeInTheDocument();
  });

  it("shows Bot icon for AI messages", () => {
    const { container } = render(<ChatMessageBubble message={aiMessage} />);
    expect(container.querySelectorAll("svg").length).toBeGreaterThan(0);
  });

  it("shows User icon for user messages", () => {
    const { container } = render(<ChatMessageBubble message={userMessage} />);
    expect(container.querySelectorAll("svg").length).toBeGreaterThan(0);
  });

  it("renders AI message aligned to start", () => {
    const { container } = render(<ChatMessageBubble message={aiMessage} />);
    const outer = container.firstChild as HTMLElement;
    expect(outer.className).toContain("justify-start");
  });

  it("renders user message aligned to end", () => {
    const { container } = render(<ChatMessageBubble message={userMessage} />);
    const outer = container.firstChild as HTMLElement;
    expect(outer.className).toContain("justify-end");
  });

  it("shows streaming cursor when isStreaming is true", () => {
    const { container } = render(
      <ChatMessageBubble message={aiMessage} isStreaming={true} />
    );
    const animatedSpan = container.querySelector(".animate-pulse");
    expect(animatedSpan).toBeInTheDocument();
  });

  it("does not show streaming cursor when isStreaming is false", () => {
    const { container } = render(
      <ChatMessageBubble message={aiMessage} isStreaming={false} />
    );
    expect(container.querySelector(".animate-pulse")).not.toBeInTheDocument();
  });

  it("applies different background classes for AI vs user", () => {
    const { container: aiContainer } = render(
      <ChatMessageBubble message={aiMessage} />
    );
    expect(aiContainer.querySelector(".bg-muted")).toBeInTheDocument();

    const { container: userContainer } = render(
      <ChatMessageBubble message={userMessage} />
    );
    expect(userContainer.querySelector(".bg-primary")).toBeInTheDocument();
  });
});
