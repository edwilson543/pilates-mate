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

export default function GenerateLessonPlanPage() {
  const router = useRouter();
  const generateMutation = useGenerateLessonPlan();

  const form = useForm<LessonPlanFormData>({
    resolver: zodResolver(lessonPlanFormSchema),
    defaultValues: {
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
      <PageHeader title="Generate Lesson Plan" />
      <Card className="max-w-2xl">
        <CardContent className="pt-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="user_prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Lesson Plan Prompt</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Describe the focus, difficulty level, and any specific requirements for your lesson plan..."
                        rows={8}
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Describe the focus, difficulty level, and any specific
                      requirements for your lesson plan (20-1000 characters)
                    </FormDescription>
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
                  Generate Lesson Plan
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
