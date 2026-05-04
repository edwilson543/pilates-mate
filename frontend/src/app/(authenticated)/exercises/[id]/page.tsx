"use client";

import { PageHeader } from "@/components/common/page-header";
import { useExercise } from "@/hooks/queries/useExercise";
import { ExerciseCard } from "@/app/(authenticated)/exercises/[id]/exercise-card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { use } from "react";

export default function ExerciseDetailPage({
  params,
}: {
  params: Promise<{ id: number }>;
}) {
  const router = useRouter();

  const { id: exerciseId } = use(params);
  const { data: exercise, isLoading, error } = useExercise(exerciseId);

  if (isLoading) {
    return (
      <div className="p-8">
        <Skeleton className="h-8 w-48 mb-6" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !exercise) {
    return (
      <div className="p-8">
        <PageHeader title="Exercise not found" />
        <div className="text-center py-12">
          <p className="text-destructive mb-4">
            The exercise you&apos;re looking for could not be found.
          </p>
          <Button onClick={() => router.push("/exercises")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to exercises
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <Button
        variant="ghost"
        onClick={() => router.push("/exercises")}
        className="mb-4"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to exercises
      </Button>
      <PageHeader
        title={exercise.name}
        actionButton={{
          label: "Edit exercise",
          onClick: () => router.push(`/exercises/${exerciseId}/edit`),
        }}
      />
      <ExerciseCard exercise={exercise} />
    </div>
  );
}
