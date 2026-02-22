import { z } from "zod";

export const exerciseFormSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().min(1, "Description is required"),
  category: z.enum(["BREATH_WORK", "STRETCH", "MOBILITY", "EFFORT"]),
  difficulty: z.enum(["BEGINNER", "INTERMEDIATE", "ADVANCED"]),
  primary_muscle_group: z.enum([
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
  starting_position: z.enum([
    "SUPINE",
    "PRONE",
    "SIDE_LYING",
    "SEATED",
    "QUADRUPED",
    "STANDING",
    "KNEELING",
    "PLANK",
    "SIDE_KNEELING",
  ]),
  variants: z
    .array(z.enum(["STANDARD", "PULSE", "HOLD"]))
    .min(1, "At least one variant is required"),
});

export type ExerciseFormData = z.infer<typeof exerciseFormSchema>;
