import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateExerciseExercisesExerciseIdPut } from "@/lib/apiClient";
import { toast } from "sonner";
import type { ExerciseFormData } from "@/lib/schemas/exercise-schema";

export function useUpdateExercise() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      data,
    }: {
      id: number;
      data: ExerciseFormData;
    }) => {
      await updateExerciseExercisesExerciseIdPut({
        path: { exercise_id: id },
        body: data,
        throwOnError: true,
      });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["exercises"] });
      queryClient.invalidateQueries({ queryKey: ["exercises", variables.id] });
      // Important: Invalidate lesson plans due to denormalized exercise data
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Exercise updated successfully");
    },
    onError: () => {
      toast.error("Failed to update exercise");
    },
  });
}
