import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteLessonPlanLessonPlansLessonPlanIdDelete } from "@/lib/apiClient";
import { toast } from "sonner";

export function useDeleteLessonPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (lessonPlanId: number) => {
      await deleteLessonPlanLessonPlansLessonPlanIdDelete({
        path: { lesson_plan_id: lessonPlanId },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Lesson plan deleted successfully");
    },
    onError: () => {
      toast.error("Failed to delete lesson plan");
    },
  });
}
