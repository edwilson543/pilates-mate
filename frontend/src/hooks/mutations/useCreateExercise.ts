import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createExerciseExercisesPost } from "@/lib/apiClient";
import { toast } from "sonner";
import type { ExerciseFormData } from "@/lib/schemas/exercise-schema";

export function useCreateExercise() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ExerciseFormData) => {
      const response = await createExerciseExercisesPost({
        body: data,
        throwOnError: true,
      });
      return response.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["exercises"] });
      toast.success("Exercise created successfully");
    },
    onError: () => {
      toast.error("Failed to create exercise");
    },
  });
}
