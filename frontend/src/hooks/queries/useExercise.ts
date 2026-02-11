import { useQuery } from "@tanstack/react-query";
import { getExerciseExercisesExerciseIdGet } from "@/lib/apiClient";

export function useExercise(id: number) {
  return useQuery({
    queryKey: ["exercises", id],
    queryFn: async () => {
      const response = await getExerciseExercisesExerciseIdGet({
        path: { exercise_id: id },
        throwOnError: true,
      });
      return response.data!;
    },
  });
}
