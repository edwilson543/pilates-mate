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

  available_equipment: z.array(
    z.enum(["BALL", "BAND", "RING", "ANKLE_WEIGHTS", "HAND_WEIGHTS"]),
  ),

  example_lesson_plan_ids: z.array(z.number()).default([]).optional(),

  user_prompt: z
    .string()
    .max(1000, "Prompt must be no more than 1000 characters"),
});

export type LessonPlanFormData = z.infer<typeof lessonPlanFormSchema>;
