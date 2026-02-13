import { useQuery } from "@tanstack/react-query";
import { getExercisesExercisesGet } from "@/lib/apiClient";

export function useExercises() {
  return useQuery({
    queryKey: ["exercises"],
    queryFn: async () => {
      const response = await getExercisesExercisesGet({
        throwOnError: true,
      });
      return response.data ?? [];
    },
  });
}
