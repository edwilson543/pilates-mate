import { z } from "zod";

export const lessonPlanFormSchema = z.object({
  duration_minutes: z
    .number()
    .int()
    .min(10, "Duration must be at least 10 minutes")
    .max(60, "Duration must be no more than 60 minutes"),

  target_difficulty: z.enum(["BEGINNER", "INTERMEDIATE", "ADVANCED"]),

  target_muscle_groups: z
    .array(
      z.enum([
        "CORE",
        "GLUTES",
        "HIP_FLEXORS",
        "BACK_EXTENSORS",
        "SHOULDERS",
        "INNER_THIGHS",
        "HAMSTRINGS",
        "OBLIQUES",
        "TRICEPS",
        "CHEST",
      ]),
    )
    .min(1, "Select at least one muscle group"),

  user_prompt: z
    .string()
    .min(20, "Prompt must be at least 20 characters")
    .max(1000, "Prompt must be no more than 1000 characters"),
});

export type LessonPlanFormData = z.infer<typeof lessonPlanFormSchema>;
