import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateExerciseSequenceLessonPlansSequencesSequenceIdPut } from "@/lib/apiClient";
import { toast } from "sonner";

export function useUpdateExerciseSequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      sequenceId,
      name,
      reps,
      notes,
    }: {
      sequenceId: number;
      name: string;
      reps: number;
      notes: string;
    }) => {
      await updateExerciseSequenceLessonPlansSequencesSequenceIdPut({
        path: { sequence_id: sequenceId },
        body: {
          name,
          reps,
          notes,
        },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Sequence updated successfully");
    },
    onError: () => {
      toast.error("Failed to update sequence");
    },
  });
}
