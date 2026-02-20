"use client";

import { PageHeader } from "@/components/common/page-header";
import { type ExerciseFormData } from "@/lib/schemas/exercise-schema";
import { useUpdateExercise } from "@/hooks/mutations/useUpdateExercise";
import { useRouter } from "next/navigation";
import { ExerciseForm } from "../../exercise-form";
import { useExercise } from "@/hooks/queries/useExercise";
import { Skeleton } from "@/components/ui/skeleton";
import { use } from "react";

export default function EditExercisePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const router = useRouter();
  const { id } = use(params);
  const exerciseId = parseInt(id);
  const { data: exercise, isLoading, error } = useExercise(exerciseId);
  const updateExerciseMutation = useUpdateExercise();

  const handleSubmit = async (data: ExerciseFormData) => {
    await updateExerciseMutation.mutateAsync({ id: exerciseId, data });
    router.push(`/exercises/${exerciseId}`);
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <Skeleton className="h-8 w-48 mb-6" />
        <Skeleton className="h-96 max-w-2xl" />
      </div>
    );
  }

  if (error || !exercise) {
    return (
      <div className="p-8">
        <PageHeader title="Edit Exercise" />
        <p className="text-red-500">Failed to load exercise</p>
        <button
          onClick={() => router.push("/exercises")}
          className="mt-4 underline"
        >
          Back to exercises
        </button>
      </div>
    );
  }

  return (
    <div className="p-8">
      <PageHeader title="Edit Exercise" />
      <ExerciseForm
        defaultValues={exercise}
        onSubmit={handleSubmit}
        onCancel={() => router.push(`/exercises/${exerciseId}`)}
        submitLabel="Save Changes"
        isPending={updateExerciseMutation.isPending}
      />
    </div>
  );
}
