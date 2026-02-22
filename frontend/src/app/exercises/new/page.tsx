"use client";

import { PageHeader } from "@/components/common/page-header";
import { type ExerciseFormData } from "@/lib/schemas/exercise-schema";
import { useCreateExercise } from "@/hooks/mutations/useCreateExercise";
import { useRouter } from "next/navigation";
import { ExerciseForm } from "../exercise-form";

export default function NewExercisePage() {
  const router = useRouter();
  const createExerciseMutation = useCreateExercise();

  const handleSubmit = async (data: ExerciseFormData) => {
    await createExerciseMutation.mutateAsync(data);
    router.push("/exercises");
  };

  return (
    <div className="p-8">
      <PageHeader title="Create exercise" />
      <ExerciseForm
        onSubmit={handleSubmit}
        onCancel={() => router.push("/exercises")}
        submitLabel="Create exercise"
        isPending={createExerciseMutation.isPending}
      />
    </div>
  );
}
