"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function InterviewPrepDetailRedirect() {
  const router = useRouter();
  useEffect(() => { router.replace("/mock-interview"); }, [router]);
  return null;
}
