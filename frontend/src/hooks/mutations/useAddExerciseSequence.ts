import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  addSequenceToSectionLessonPlansLessonPlanIdSequencesPost,
  type LessonPlanSection,
} from "@/lib/apiClient";
import { toast } from "sonner";

export function useAddExerciseSequence() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      lessonPlanId,
      section,
      name,
      reps,
      notes,
    }: {
      lessonPlanId: number;
      section: LessonPlanSection;
      name: string;
      reps: number;
      notes: string;
    }) => {
      await addSequenceToSectionLessonPlansLessonPlanIdSequencesPost({
        path: { lesson_plan_id: lessonPlanId },
        body: {
          section,
          name,
          reps,
          notes,
        },
        throwOnError: true,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-plans"] });
      toast.success("Sequence added successfully");
    },
    onError: () => {
      toast.error("Failed to add sequence");
    },
  });
}
