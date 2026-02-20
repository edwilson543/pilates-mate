import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteExerciseSetLessonPlansSequencesSequenceIdSetsSetIdDelete } from "@/lib/apiClient";
import { toast } from "sonner";

export function useDeleteExerciseSet() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      sequenceId,
      setId,
    }: {
      sequenceId: number;
      setId: number;
    }) => {
      await deleteExerciseSetLessonPlansSequencesSequenceIdSetsSetIdDelete({
        path: { sequence_id: sequenceId, set_id: setId },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Set deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete set");
    },
  });
}
