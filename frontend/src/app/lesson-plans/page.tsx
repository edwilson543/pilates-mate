"use client";

import { PageHeader } from "@/components/common/page-header";
import { useLessonPlans } from "@/hooks/queries/useLessonPlans";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import { useDeleteLessonPlan } from "@/hooks/mutations/useDeleteLessonPlan";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useState } from "react";

export default function LessonPlansPage() {
  const router = useRouter();
  const { data: lessonPlans, isLoading, error } = useLessonPlans();
  const deleteLessonPlan = useDeleteLessonPlan();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [planToDelete, setPlanToDelete] = useState<number | null>(null);

  const handleDelete = (planId: number) => {
    deleteLessonPlan.mutate(planId, {
      onSuccess: () => {
        setDeleteDialogOpen(false);
        setPlanToDelete(null);
      },
    });
  };

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
            className="group cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => router.push(`/lesson-plans/${plan.id}`)}
          >
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle>{plan.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {new Date(plan.date).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </p>
                </div>
                <AlertDialog
                  open={deleteDialogOpen && planToDelete === plan.id}
                  onOpenChange={(open) => {
                    setDeleteDialogOpen(open);
                    if (!open) setPlanToDelete(null);
                  }}
                >
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => {
                        e.stopPropagation();
                        setPlanToDelete(plan.id);
                        setDeleteDialogOpen(true);
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete lesson plan?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will permanently delete &quot;{plan.name}&quot;.
                        This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction onClick={() => handleDelete(plan.id)}>
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
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
