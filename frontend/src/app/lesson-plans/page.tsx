"use client";

import { PageHeader } from "@/components/custom/page-header";
import { useLessonPlans } from "@/hooks/queries/useLessonPlans";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function LessonPlansPage() {
  const router = useRouter();
  const { data: lessonPlans, isLoading, error } = useLessonPlans();

  if (isLoading) {
    return (
      <div className="p-8">
        <PageHeader title="Lesson Plans" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <PageHeader title="Lesson Plans" />
        <div className="text-center py-12">
          <p className="text-destructive">Failed to load lesson plans</p>
        </div>
      </div>
    );
  }

  if (!lessonPlans || lessonPlans.length === 0) {
    return (
      <div className="p-8">
        <PageHeader title="Lesson Plans" />
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">
            No lesson plans found. Generate your first lesson plan to get
            started.
          </p>
          <Button onClick={() => router.push("/lesson-plans/generate")}>
            Generate Lesson Plan
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Lesson Plans"
        actionButton={{
          label: "Generate Lesson Plan",
          onClick: () => router.push("/lesson-plans/generate"),
        }}
      />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {lessonPlans.map((plan) => (
          <Card
            key={plan.id}
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => router.push(`/lesson-plans/${plan.id}`)}
          >
            <CardHeader>
              <CardTitle>{plan.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground line-clamp-3">
                {plan.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
