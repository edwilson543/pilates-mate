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
import { useLessonPlans } from "@/hooks/queries/useLessonPlans";
import {
  Combobox,
  ComboboxChips,
  ComboboxChip,
  ComboboxChipsInput,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxItem,
  ComboboxList,
  useComboboxAnchor,
} from "@/components/ui/combobox";

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

const equipmentOptions = [
  { id: "BALL", label: "Ball" },
  { id: "BAND", label: "Band" },
  { id: "RING", label: "Ring" },
  { id: "ANKLE_WEIGHTS", label: "Ankle Weights" },
  { id: "HAND_WEIGHTS", label: "Hand Weights" },
] as const;

export default function GenerateLessonPlanPage() {
  const router = useRouter();
  const generateMutation = useGenerateLessonPlan();
  const { data: lessonPlans, isLoading: isLoadingLessonPlans } =
    useLessonPlans();
  const [duration, setDuration] = useState(45);
  const [difficultyIndex, setDifficultyIndex] = useState(1);
  const comboboxAnchor = useComboboxAnchor();

  const form = useForm<LessonPlanFormData>({
    resolver: zodResolver(lessonPlanFormSchema),
    defaultValues: {
      duration_minutes: 45,
      target_difficulty: "INTERMEDIATE",
      target_muscle_groups: [],
      available_equipment: [],
      example_lesson_plan_ids: [],
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
    <div className="p-8 pb-16">
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
                          disabled={generateMutation.isPending}
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
                          disabled={generateMutation.isPending}
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
                                  disabled={generateMutation.isPending}
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
                name="available_equipment"
                render={() => (
                  <FormItem>
                    <FormLabel>Available equipment</FormLabel>
                    <div className="space-y-2">
                      {equipmentOptions.map((equipment) => (
                        <FormField
                          key={equipment.id}
                          control={form.control}
                          name="available_equipment"
                          render={({ field }) => (
                            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                              <FormControl>
                                <Checkbox
                                  checked={field.value?.includes(equipment.id)}
                                  onCheckedChange={(checked) => {
                                    return checked
                                      ? field.onChange([
                                          ...field.value,
                                          equipment.id,
                                        ])
                                      : field.onChange(
                                          field.value?.filter(
                                            (value) => value !== equipment.id,
                                          ),
                                        );
                                  }}
                                  disabled={generateMutation.isPending}
                                />
                              </FormControl>
                              <FormLabel className="font-normal cursor-pointer">
                                {equipment.label}
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
                defaultValue={""}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Additional requirements</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Build my booty to the maximum..."
                        rows={5}
                        {...field}
                        disabled={generateMutation.isPending}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="example_lesson_plan_ids"
                render={({ field }) => {
                  const availablePlans = lessonPlans || [];
                  const selectedIds = field.value || [];

                  const unselectedPlans = availablePlans.filter(
                    (plan) => !selectedIds.includes(plan.id),
                  );

                  const selectedPlans = availablePlans.filter((plan) =>
                    selectedIds.includes(plan.id),
                  );

                  return (
                    <FormItem>
                      <FormLabel>Example lesson plans</FormLabel>
                      <FormDescription>
                        Select lesson plans to use as examples. The three most
                        recent plans will be used by default.
                      </FormDescription>
                      <FormControl>
                        <Combobox
                          value={selectedIds.map(String)}
                          onValueChange={(values) => {
                            field.onChange(values.map(Number));
                          }}
                          multiple
                          disabled={
                            generateMutation.isPending || isLoadingLessonPlans
                          }
                        >
                          <ComboboxChips ref={comboboxAnchor}>
                            {selectedPlans.map((plan) => (
                              <ComboboxChip key={plan.id}>
                                {plan.name}
                              </ComboboxChip>
                            ))}
                            <ComboboxChipsInput
                              placeholder={
                                selectedIds.length === 0
                                  ? "Search lesson plans..."
                                  : undefined
                              }
                            />
                          </ComboboxChips>
                          <ComboboxContent anchor={comboboxAnchor}>
                            <ComboboxList>
                              {isLoadingLessonPlans ? (
                                <div className="p-2 text-sm text-muted-foreground text-center">
                                  Loading lesson plans...
                                </div>
                              ) : unselectedPlans.length === 0 &&
                                selectedIds.length === 0 ? (
                                <ComboboxEmpty>
                                  No lesson plans available. Generate your first
                                  plan to use as an example.
                                </ComboboxEmpty>
                              ) : unselectedPlans.length === 0 ? (
                                <ComboboxEmpty>
                                  All lesson plans selected
                                </ComboboxEmpty>
                              ) : (
                                unselectedPlans.map((plan) => (
                                  <ComboboxItem
                                    key={plan.id}
                                    value={String(plan.id)}
                                  >
                                    <div className="flex flex-col">
                                      <span className="font-medium">
                                        {plan.name}
                                      </span>
                                      <span className="text-xs text-muted-foreground">
                                        {new Date(plan.date).toLocaleDateString(
                                          "en-US",
                                          {
                                            year: "numeric",
                                            month: "short",
                                            day: "numeric",
                                          },
                                        )}
                                      </span>
                                    </div>
                                  </ComboboxItem>
                                ))
                              )}
                            </ComboboxList>
                          </ComboboxContent>
                        </Combobox>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  );
                }}
              />

              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push("/lesson-plans")}
                  disabled={generateMutation.isPending}
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
