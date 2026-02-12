"use client";

import { PageHeader } from "@/components/custom/page-header";
import { use } from "react";
import { useLessonPlan } from "@/hooks/queries/useLessonPlan";
import { ExerciseSequenceCard } from "@/components/custom/exercise-sequence-card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";

export default function LessonPlanDetailPage({
  params,
}: {
  params: Promise<{ id: number }>;
}) {
  const router = useRouter();

  const { id: lessonPlanId } = use(params);
  const { data: lessonPlan, isLoading, error } = useLessonPlan(lessonPlanId);

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
            Back to Lesson Plans
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <Button
        variant="ghost"
        onClick={() => router.push("/lesson-plans")}
        className="mb-4"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Lesson Plans
      </Button>
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
                <ExerciseSequenceCard
                  key={index}
                  sequence={sequence}
                  index={index}
                />
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
                <ExerciseSequenceCard
                  key={index}
                  sequence={sequence}
                  index={index}
                />
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
                <ExerciseSequenceCard
                  key={index}
                  sequence={sequence}
                  index={index}
                />
              ))}
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
