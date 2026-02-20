import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  updateExerciseSetLessonPlansSequencesSequenceIdSetsSetIdPut,
  type ExerciseVariant,
} from "@/lib/apiClient";
import { toast } from "sonner";

export function useUpdateExerciseSet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      sequenceId,
      setId,
      reps,
      durationSeconds,
      variant,
    }: {
      sequenceId: number;
      setId: number;
      reps: number;
      durationSeconds: number;
      variant: ExerciseVariant;
    }) => {
      await updateExerciseSetLessonPlansSequencesSequenceIdSetsSetIdPut({
        path: { sequence_id: sequenceId, set_id: setId },
        body: {
          reps,
          duration_seconds: durationSeconds,
          variant,
        },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Set updated successfully");
    },
    onError: () => {
      toast.error("Failed to update set");
    },
  });
}
