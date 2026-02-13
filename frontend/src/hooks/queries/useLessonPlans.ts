import { useQuery } from "@tanstack/react-query";
import { getLessonPlansLessonPlansGet } from "@/lib/apiClient";

export function useLessonPlans() {
  return useQuery({
    queryKey: ["lesson-plans"],
    queryFn: async () => {
      const response = await getLessonPlansLessonPlansGet({
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });
}
