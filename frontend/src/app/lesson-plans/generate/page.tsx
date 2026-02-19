"use client";

import { PageHeader } from "@/components/common/page-header";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  lessonPlanFormSchema,
  type LessonPlanFormData,
} from "@/lib/schemas/lesson-plan-schema";
import { useGenerateLessonPlan } from "@/hooks/mutations/useGenerateLessonPlan";
import { useRouter } from "next/navigation";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2 } from "lucide-react";
import { Slider } from "@/components/ui/slider";
import { Checkbox } from "@/components/ui/checkbox";
import { useState } from "react";

const muscleGroups = [
  { value: "CORE", label: "Core" },
  { value: "GLUTES", label: "Glutes" },
  { value: "HIP_FLEXORS", label: "Hip Flexors" },
  { value: "BACK_EXTENSORS", label: "Back Extensors" },
  { value: "SHOULDERS", label: "Shoulders" },
  { value: "INNER_THIGHS", label: "Inner Thighs" },
  { value: "HAMSTRINGS", label: "Hamstrings" },
  { value: "OBLIQUES", label: "Obliques" },
  { value: "TRICEPS", label: "Triceps" },
  { value: "CHEST", label: "Chest" },
] as const;

const difficultyLevels = ["BEGINNER", "INTERMEDIATE", "ADVANCED"] as const;
const difficultyLabels = ["Beginner", "Intermediate", "Advanced"];

export default function GenerateLessonPlanPage() {
  const router = useRouter();
  const generateMutation = useGenerateLessonPlan();
  const [duration, setDuration] = useState(45);
  const [difficultyIndex, setDifficultyIndex] = useState(1);

  const form = useForm<LessonPlanFormData>({
    resolver: zodResolver(lessonPlanFormSchema),
    defaultValues: {
      duration_minutes: 45,
      target_difficulty: "INTERMEDIATE",
      target_muscle_groups: [],
      user_prompt: "",
    },
  });

  const onSubmit = async (data: LessonPlanFormData) => {
    const result = await generateMutation.mutateAsync(data);
    if (result?.lesson_plan?.id) {
      router.push(`/lesson-plans/${result.lesson_plan.id}`);
    }
  };

  return (
    <div className="p-8">
      <PageHeader title="Generate lesson plan" />
      <Card className="w-full">
        <CardContent className="pt-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="duration_minutes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Duration (minutes)</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={10}
                          max={60}
                          step={5}
                          value={[duration]}
                          onValueChange={(value) => {
                            const newDuration = value[0];
                            setDuration(newDuration);
                            field.onChange(newDuration);
                          }}
                        />
                        <div className="text-sm text-center font-medium">
                          {duration} minutes
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="target_difficulty"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Difficulty Level</FormLabel>
                    <FormControl>
                      <div className="space-y-2">
                        <Slider
                          min={0}
                          max={2}
                          step={1}
                          value={[difficultyIndex]}
                          onValueChange={(value) => {
                            const index = value[0];
                            setDifficultyIndex(index);
                            field.onChange(difficultyLevels[index]);
                          }}
                        />
                        <div className="text-sm text-center font-medium">
                          {difficultyLabels[difficultyIndex]}
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="target_muscle_groups"
                render={() => (
                  <FormItem>
                    <FormLabel>Target Muscle Groups</FormLabel>
                    <div className="grid grid-cols-2 gap-4">
                      {muscleGroups.map((group) => (
                        <FormField
                          key={group.value}
                          control={form.control}
                          name="target_muscle_groups"
                          render={({ field }) => (
                            <FormItem className="flex items-center space-x-2 space-y-0">
                              <FormControl>
                                <Checkbox
                                  checked={field.value?.includes(group.value)}
                                  onCheckedChange={(checked) => {
                                    const currentValue = field.value || [];
                                    if (checked) {
                                      field.onChange([
                                        ...currentValue,
                                        group.value,
                                      ]);
                                    } else {
                                      field.onChange(
                                        currentValue.filter(
                                          (val) => val !== group.value,
                                        ),
                                      );
                                    }
                                  }}
                                />
                              </FormControl>
                              <FormLabel className="font-normal cursor-pointer">
                                {group.label}
                              </FormLabel>
                            </FormItem>
                          )}
                        />
                      ))}
                    </div>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="user_prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Additional requirements</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Build my booty to the maximum..."
                        rows={5}
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push("/lesson-plans")}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={generateMutation.isPending}>
                  {generateMutation.isPending && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Generate
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
