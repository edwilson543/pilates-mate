"use client";

import { PageHeader } from "@/components/common/page-header";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  exerciseFormSchema,
  type ExerciseFormData,
} from "@/lib/schemas/exercise-schema";
import { useCreateExercise } from "@/hooks/mutations/useCreateExercise";
import { useRouter } from "next/navigation";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";

export default function NewExercisePage() {
  const router = useRouter();
  const createExerciseMutation = useCreateExercise();

  const form = useForm<ExerciseFormData>({
    resolver: zodResolver(exerciseFormSchema),
    defaultValues: {
      name: "",
      description: "",
      difficulty: "BEGINNER",
      primary_muscle_group: "CORE",
      starting_position: "SUPINE",
    },
  });

  const onSubmit = async (data: ExerciseFormData) => {
    await createExerciseMutation.mutateAsync(data);
    router.push("/exercises");
  };

  return (
    <div className="p-8">
      <PageHeader title="Create Exercise" />
      <Card className="max-w-2xl">
        <CardContent className="pt-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Exercise name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Describe the exercise"
                        rows={4}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="difficulty"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Difficulty</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select difficulty" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="BEGINNER">Beginner</SelectItem>
                        <SelectItem value="INTERMEDIATE">
                          Intermediate
                        </SelectItem>
                        <SelectItem value="ADVANCED">Advanced</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="primary_muscle_group"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Primary Muscle Group</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select muscle group" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="CORE">Core</SelectItem>
                        <SelectItem value="GLUTES">Glutes</SelectItem>
                        <SelectItem value="HIP_FLEXORS">Hip Flexors</SelectItem>
                        <SelectItem value="BACK_EXTENSORS">
                          Back Extensors
                        </SelectItem>
                        <SelectItem value="SHOULDERS">Shoulders</SelectItem>
                        <SelectItem value="INNER_THIGHS">
                          Inner Thighs
                        </SelectItem>
                        <SelectItem value="HAMSTRINGS">Hamstrings</SelectItem>
                        <SelectItem value="OBLIQUES">Obliques</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="starting_position"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Starting Position</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select starting position" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="SUPINE">Supine</SelectItem>
                        <SelectItem value="PRONE">Prone</SelectItem>
                        <SelectItem value="SIDE_LYING">Side Lying</SelectItem>
                        <SelectItem value="SEATED">Seated</SelectItem>
                        <SelectItem value="QUADRUPED">Quadruped</SelectItem>
                        <SelectItem value="STANDING">Standing</SelectItem>
                        <SelectItem value="KNEELING">Kneeling</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push("/exercises")}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={createExerciseMutation.isPending}
                >
                  {createExerciseMutation.isPending && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Create Exercise
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
