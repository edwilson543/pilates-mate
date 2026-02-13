import { z } from "zod";

export const lessonPlanFormSchema = z.object({
  user_prompt: z
    .string()
    .min(20, "Prompt must be at least 20 characters")
    .max(1000, "Prompt must be no more than 1000 characters"),
});

export type LessonPlanFormData = z.infer<typeof lessonPlanFormSchema>;
