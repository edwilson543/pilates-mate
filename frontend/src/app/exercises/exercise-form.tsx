"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  exerciseFormSchema,
  type ExerciseFormData,
} from "@/lib/schemas/exercise-schema";
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
import { Checkbox } from "@/components/ui/checkbox";
import { Loader2 } from "lucide-react";

interface ExerciseFormProps {
  defaultValues?: ExerciseFormData;
  onSubmit: (data: ExerciseFormData) => Promise<void>;
  onCancel: () => void;
  submitLabel: string;
  isPending?: boolean;
}

export function ExerciseForm({
  defaultValues,
  onSubmit,
  onCancel,
  submitLabel,
  isPending = false,
}: ExerciseFormProps) {
  const form = useForm<ExerciseFormData>({
    resolver: zodResolver(exerciseFormSchema),
    defaultValues: defaultValues || {
      name: "",
      description: "",
      category: "EFFORT",
      difficulty: "BEGINNER",
      primary_muscle_group: "CORE",
      starting_position: "SUPINE",
      movement_variants: ["STANDARD"],
    },
  });

  return (
    <Card className="w-full">
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

            <div className={"flex flex-row justify-between"}>
              <FormField
                control={form.control}
                name="category"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Category</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="BREATH_WORK">Breath Work</SelectItem>
                        <SelectItem value="STRETCH">Stretch</SelectItem>
                        <SelectItem value="MOBILITY">Mobility</SelectItem>
                        <SelectItem value="EFFORT">Effort</SelectItem>
                      </SelectContent>
                    </Select>
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
                    <FormLabel>Primary muscle group</FormLabel>
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
                        <SelectItem value="TRICEPS">Triceps</SelectItem>
                        <SelectItem value="CHEST">Chest</SelectItem>
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
                    <FormLabel>Starting position</FormLabel>
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
                        <SelectItem value="PLANK">Plank</SelectItem>
                        <SelectItem value="SIDE_KNEELING">
                          Side Kneeling
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="movement_variants"
              render={() => (
                <FormItem>
                  <div className="mb-4">
                    <FormLabel>Movements</FormLabel>
                  </div>
                  {(
                    [
                      { id: "STANDARD", label: "Standard" },
                      { id: "PULSE", label: "Pulse" },
                      { id: "HOLD", label: "Hold" },
                    ] as const
                  ).map((movement_variant) => (
                    <FormField
                      key={movement_variant.id}
                      control={form.control}
                      name="movement_variants"
                      render={({ field }) => {
                        return (
                          <FormItem
                            key={movement_variant.id}
                            className="flex flex-row items-start space-x-3 space-y-0"
                          >
                            <FormControl>
                              <Checkbox
                                checked={field.value?.includes(
                                  movement_variant.id,
                                )}
                                onCheckedChange={(checked) => {
                                  return checked
                                    ? field.onChange([
                                        ...field.value,
                                        movement_variant.id,
                                      ])
                                    : field.onChange(
                                        field.value?.filter(
                                          (value) =>
                                            value !== movement_variant.id,
                                        ),
                                      );
                                }}
                              />
                            </FormControl>
                            <FormLabel className="font-normal">
                              {movement_variant.label}
                            </FormLabel>
                          </FormItem>
                        );
                      }}
                    />
                  ))}
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex gap-4">
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
              <Button type="submit" disabled={isPending}>
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {submitLabel}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
