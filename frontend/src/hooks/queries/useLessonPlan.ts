import { useQuery } from "@tanstack/react-query";
import { getLessonPlanLessonPlansLessonPlanIdGet } from "@/lib/apiClient";

export function useLessonPlan(id: number) {
  return useQuery({
    queryKey: ["lesson-plans", id],
    queryFn: async () => {
      const response = await getLessonPlanLessonPlansLessonPlanIdGet({
        path: { lesson_plan_id: id },
        throwOnError: true,
      });
      return response.data!;
    },
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "PENDING_GENERATION" ? 2000 : false;
    },
  });
}
