import { z } from "zod";

export const exerciseFormSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().min(1, "Description is required"),
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
  ]),
  starting_position: z.enum([
    "SUPINE",
    "PRONE",
    "SIDE_LYING",
    "SEATED",
    "QUADRUPED",
    "STANDING",
    "KNEELING",
  ]),
});

export type ExerciseFormData = z.infer<typeof exerciseFormSchema>;
