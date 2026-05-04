import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Lesson plans",
  description: "Browse and manage pilates lesson plans",
};

export default function LessonPlansLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
