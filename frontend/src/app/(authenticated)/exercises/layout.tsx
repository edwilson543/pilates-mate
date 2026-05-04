import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Exercises",
  description: "Browse and manage pilates exercises",
};

export default function ExercisesLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
