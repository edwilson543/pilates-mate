import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  addSetToSequenceLessonPlansSequencesSequenceIdSetsPost,
  type MovementVariant,
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
      movement_variant,
    }: {
      sequenceId: number;
      exerciseId: number;
      reps: number;
      durationSeconds: number;
      movement_variant: MovementVariant;
    }) => {
      await addSetToSequenceLessonPlansSequencesSequenceIdSetsPost({
        path: { sequence_id: sequenceId },
        body: {
          exercise_id: exerciseId,
          reps,
          duration_seconds: durationSeconds,
          movement_variant,
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
