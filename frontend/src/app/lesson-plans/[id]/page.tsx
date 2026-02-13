"use client";

import { PageHeader } from "@/components/common/page-header";
import { use, useState } from "react";
import { useLessonPlan } from "@/hooks/queries/useLessonPlan";
import { ExerciseSequenceCard } from "@/app/lesson-plans/[id]/exercise-sequence-card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { ArrowLeft, Trash2 } from "lucide-react";
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

export default function LessonPlanDetailPage({
  params,
}: {
  params: Promise<{ id: number }>;
}) {
  const router = useRouter();
  const deleteLessonPlan = useDeleteLessonPlan();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { id: lessonPlanId } = use(params);
  const { data: lessonPlan, isLoading, error } = useLessonPlan(lessonPlanId);

  const handleDelete = () => {
    deleteLessonPlan.mutate(lessonPlanId, {
      onSuccess: () => {
        router.push("/lesson-plans");
      },
    });
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <Skeleton className="h-8 w-48 mb-6" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !lessonPlan) {
    return (
      <div className="p-8">
        <PageHeader title="Lesson Plan Not Found" />
        <div className="text-center py-12">
          <p className="text-destructive mb-4">
            The lesson plan you&apos;re looking for could not be found.
          </p>
          <Button onClick={() => router.push("/lesson-plans")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to lesson plans
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-4">
        <Button variant="ghost" onClick={() => router.push("/lesson-plans")}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to lesson plans
        </Button>
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogTrigger asChild>
            <Button variant="destructive">
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete lesson plan?</AlertDialogTitle>
              <AlertDialogDescription>
                This will permanently delete &quot;{lessonPlan.name}&quot;. This
                action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleDelete}>
                Delete
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
      <div>
        <PageHeader
          title={lessonPlan.name}
          description={lessonPlan.description}
        />
        <p className="text-sm text-muted-foreground mb-6 -mt-2">
          {new Date(lessonPlan.date).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      <Accordion
        type="multiple"
        defaultValue={["warm-up", "main", "cool-down"]}
        className="space-y-4"
      >
        <AccordionItem value="warm-up">
          <AccordionTrigger className="text-lg font-semibold">
            Warm Up
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 pt-4">
              {lessonPlan.warm_up.map((sequence, index) => (
                <ExerciseSequenceCard key={index} sequence={sequence} />
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="main">
          <AccordionTrigger className="text-lg font-semibold">
            Main Session
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 pt-4">
              {lessonPlan.main_session.map((sequence, index) => (
                <ExerciseSequenceCard key={index} sequence={sequence} />
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="cool-down">
          <AccordionTrigger className="text-lg font-semibold">
            Cool Down
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 pt-4">
              {lessonPlan.cool_down.map((sequence, index) => (
                <ExerciseSequenceCard key={index} sequence={sequence} />
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
