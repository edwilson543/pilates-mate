import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  addSetToSequenceLessonPlansSequencesSequenceIdSetsPost,
  type MovementVariant,
  type Equipment,
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
      equipment_variant,
    }: {
      sequenceId: number;
      exerciseId: number;
      reps: number;
      durationSeconds: number;
      movement_variant: MovementVariant;
      equipment_variant: Equipment[];
    }) => {
      await addSetToSequenceLessonPlansSequencesSequenceIdSetsPost({
        path: { sequence_id: sequenceId },
        body: {
          exercise_id: exerciseId,
          reps,
          duration_seconds: durationSeconds,
          movement_variant,
          equipment_variant,
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
