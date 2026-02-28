import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteExerciseSequenceLessonPlansSequencesSequenceIdDelete } from "@/lib/apiClient";
import { toast } from "sonner";

export function useDeleteExerciseSequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ sequenceId }: { sequenceId: number }) => {
      await deleteExerciseSequenceLessonPlansSequencesSequenceIdDelete({
        path: { sequence_id: sequenceId },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Sequence deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete sequence");
    },
  });
}
