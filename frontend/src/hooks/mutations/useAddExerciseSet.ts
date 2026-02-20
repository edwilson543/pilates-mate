import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  addSetToSequenceLessonPlansSequencesSequenceIdSetsPost,
  type ExerciseVariant,
} from "@/lib/apiClient";
import { toast } from "sonner";

export function useAddExerciseSet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      sequenceId,
      exerciseId,
      reps,
      durationSeconds,
      variant,
    }: {
      sequenceId: number;
      exerciseId: number;
      reps: number;
      durationSeconds: number;
      variant: ExerciseVariant;
    }) => {
      await addSetToSequenceLessonPlansSequencesSequenceIdSetsPost({
        path: { sequence_id: sequenceId },
        body: {
          exercise_id: exerciseId,
          reps,
          duration_seconds: durationSeconds,
          variant,
        },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Set added successfully");
    },
    onError: () => {
      toast.error("Failed to add set");
    },
  });
}
