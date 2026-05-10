import { useMutation, useQueryClient } from "@tanstack/react-query";
import { generateLessonPlanLessonPlansPost } from "@/lib/apiClient";
import { toast } from "sonner";
import type { LessonPlanFormData } from "@/lib/schemas/lesson-plan-schema";

export function useGenerateLessonPlan() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: LessonPlanFormData) => {
      const response = await generateLessonPlanLessonPlansPost({
        body: {
          requirements: data,
        },
        throwOnError: true,
      });
      return response.data!;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Generating lesson plan...");
    },
    onError: () => {
      toast.error("Failed to generate lesson plan");
    },
  });
}
