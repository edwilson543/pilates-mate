"use client";

import { PageHeader } from "@/components/common/page-header";
import { use, useState } from "react";
import { useLessonPlan } from "@/hooks/queries/useLessonPlan";
import { ExerciseSequenceCard } from "@/app/(authenticated)/lesson-plans/[id]/exercise-sequence-card";
import { LessonPlanRequirementsTable } from "@/app/(authenticated)/lesson-plans/[id]/lesson-plan-requirements-card";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { ArrowLeft, Loader2, Trash2, PlusIcon, XIcon, CheckIcon } from "lucide-react";
import { useDeleteLessonPlan } from "@/hooks/mutations/useDeleteLessonPlan";
import { useAddExerciseSequence } from "@/hooks/mutations/useAddExerciseSequence";
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
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { LessonPlanSection } from "@/lib/apiClient/types.gen";

export default function LessonPlanDetailPage({
  params,
}: {
  params: Promise<{ id: number }>;
}) {
  const router = useRouter();
  const deleteLessonPlan = useDeleteLessonPlan();
  const addSequenceMutation = useAddExerciseSequence();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [addingSequenceToSection, setAddingSequenceToSection] =
    useState<LessonPlanSection | null>(null);
  const [newSequenceFormData, setNewSequenceFormData] = useState({
    name: "",
    reps: 1,
    notes: "",
  });

  const { id: lessonPlanId } = use(params);
  const { data: lessonPlan, isLoading, error } = useLessonPlan(lessonPlanId);

  const handleDelete = () => {
    deleteLessonPlan.mutate(lessonPlanId, {
      onSuccess: () => {
        router.push("/lesson-plans");
      },
    });
  };

  const handleAddSequenceClick = (section: LessonPlanSection) => {
    setNewSequenceFormData({
      name: "",
      reps: 1,
      notes: "",
    });
    setAddingSequenceToSection(section);
  };

  const handleCancelAddSequence = () => {
    setAddingSequenceToSection(null);
    setNewSequenceFormData({
      name: "",
      reps: 1,
      notes: "",
    });
  };

  const handleSaveNewSequence = async (section: LessonPlanSection) => {
    if (newSequenceFormData.name && newSequenceFormData.reps > 0) {
      try {
        await addSequenceMutation.mutateAsync({
          lessonPlanId: lessonPlanId,
          section: section,
          name: newSequenceFormData.name,
          reps: newSequenceFormData.reps,
          notes: newSequenceFormData.notes,
        });
        setAddingSequenceToSection(null);
        setNewSequenceFormData({
          name: "",
          reps: 1,
          notes: "",
        });
      } catch (error) {
        // Error handled by mutation
      }
    }
  };

  const isNewSequenceFormValid = () => {
    return newSequenceFormData.name.length > 0 && newSequenceFormData.reps > 0;
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

  if (lessonPlan.status === "PENDING_GENERATION") {
    return (
      <div className="p-8">
        <div className="flex items-center justify-between mb-4">
          <Button variant="ghost" onClick={() => router.push("/lesson-plans")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to lesson plans
          </Button>
        </div>
        <PageHeader title={lessonPlan.name} />
        <p className="text-sm text-muted-foreground mb-6 -mt-2">
          {new Date(lessonPlan.date).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
        <div className="flex items-center gap-3 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Generating your lesson plan...</span>
        </div>
      </div>
    );
  }

  if (lessonPlan.status === "ERRORED") {
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
                  This will permanently delete &quot;{lessonPlan.name}&quot;.
                  This action cannot be undone.
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
        <PageHeader title={lessonPlan.name} />
        <p className="text-destructive mt-2">
          An error occurred while generating this lesson plan.
        </p>
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
        <AccordionItem value="requirements">
          <AccordionTrigger className="text-lg font-semibold">
            Requirements
          </AccordionTrigger>
          <AccordionContent>
            <div className="pt-4">
              <LessonPlanRequirementsTable
                requirements={lessonPlan.requirements}
              />
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="warm-up">
          <AccordionTrigger className="text-lg font-semibold">
            Warm up
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 pt-4">
              {lessonPlan.warm_up.map((sequence, index) => (
                <ExerciseSequenceCard key={index} sequence={sequence} />
              ))}
              {addingSequenceToSection === "WARM_UP" ? (
                <Card className="border-2 border-dashed">
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="new-sequence-name">Sequence Name</Label>
                        <Input
                          id="new-sequence-name"
                          value={newSequenceFormData.name}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              name: e.target.value,
                            })
                          }
                          className="mt-1"
                          placeholder="e.g., Breathing Exercises"
                        />
                      </div>
                      <div>
                        <Label htmlFor="new-sequence-reps">Reps</Label>
                        <Input
                          id="new-sequence-reps"
                          type="number"
                          value={newSequenceFormData.reps}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              reps: Number(e.target.value),
                            })
                          }
                          className="mt-1 w-32"
                          min="1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="new-sequence-notes">Notes</Label>
                        <Textarea
                          id="new-sequence-notes"
                          value={newSequenceFormData.notes}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              notes: e.target.value,
                            })
                          }
                          className="mt-1"
                          placeholder="Optional notes..."
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleSaveNewSequence("WARM_UP")}
                          disabled={
                            !isNewSequenceFormValid() ||
                            addSequenceMutation.isPending
                          }
                        >
                          <CheckIcon className="h-4 w-4 mr-2" />
                          Add Sequence
                        </Button>
                        <Button
                          variant="outline"
                          onClick={handleCancelAddSequence}
                          disabled={addSequenceMutation.isPending}
                        >
                          <XIcon className="h-4 w-4 mr-2" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Button
                  variant="outline"
                  onClick={() => handleAddSequenceClick("WARM_UP")}
                  className="w-full"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Add Exercise Sequence
                </Button>
              )}
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="main">
          <AccordionTrigger className="text-lg font-semibold">
            Main session
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 pt-4">
              {lessonPlan.main_session.map((sequence, index) => (
                <ExerciseSequenceCard key={index} sequence={sequence} />
              ))}
              {addingSequenceToSection === "MAIN_SESSION" ? (
                <Card className="border-2 border-dashed">
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="new-sequence-name-main">
                          Sequence Name
                        </Label>
                        <Input
                          id="new-sequence-name-main"
                          value={newSequenceFormData.name}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              name: e.target.value,
                            })
                          }
                          className="mt-1"
                          placeholder="e.g., Core Strengthening"
                        />
                      </div>
                      <div>
                        <Label htmlFor="new-sequence-reps-main">Reps</Label>
                        <Input
                          id="new-sequence-reps-main"
                          type="number"
                          value={newSequenceFormData.reps}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              reps: Number(e.target.value),
                            })
                          }
                          className="mt-1 w-32"
                          min="1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="new-sequence-notes-main">Notes</Label>
                        <Textarea
                          id="new-sequence-notes-main"
                          value={newSequenceFormData.notes}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              notes: e.target.value,
                            })
                          }
                          className="mt-1"
                          placeholder="Optional notes..."
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleSaveNewSequence("MAIN_SESSION")}
                          disabled={
                            !isNewSequenceFormValid() ||
                            addSequenceMutation.isPending
                          }
                        >
                          <CheckIcon className="h-4 w-4 mr-2" />
                          Add Sequence
                        </Button>
                        <Button
                          variant="outline"
                          onClick={handleCancelAddSequence}
                          disabled={addSequenceMutation.isPending}
                        >
                          <XIcon className="h-4 w-4 mr-2" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Button
                  variant="outline"
                  onClick={() => handleAddSequenceClick("MAIN_SESSION")}
                  className="w-full"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Add Exercise Sequence
                </Button>
              )}
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="cool-down">
          <AccordionTrigger className="text-lg font-semibold">
            Cool down
          </AccordionTrigger>
          <AccordionContent>
            <div className="space-y-4 pt-4">
              {lessonPlan.cool_down.map((sequence, index) => (
                <ExerciseSequenceCard key={index} sequence={sequence} />
              ))}
              {addingSequenceToSection === "COOL_DOWN" ? (
                <Card className="border-2 border-dashed">
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="new-sequence-name-cool">
                          Sequence Name
                        </Label>
                        <Input
                          id="new-sequence-name-cool"
                          value={newSequenceFormData.name}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              name: e.target.value,
                            })
                          }
                          className="mt-1"
                          placeholder="e.g., Stretching Sequence"
                        />
                      </div>
                      <div>
                        <Label htmlFor="new-sequence-reps-cool">Reps</Label>
                        <Input
                          id="new-sequence-reps-cool"
                          type="number"
                          value={newSequenceFormData.reps}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              reps: Number(e.target.value),
                            })
                          }
                          className="mt-1 w-32"
                          min="1"
                        />
                      </div>
                      <div>
                        <Label htmlFor="new-sequence-notes-cool">Notes</Label>
                        <Textarea
                          id="new-sequence-notes-cool"
                          value={newSequenceFormData.notes}
                          onChange={(e) =>
                            setNewSequenceFormData({
                              ...newSequenceFormData,
                              notes: e.target.value,
                            })
                          }
                          className="mt-1"
                          placeholder="Optional notes..."
                        />
                      </div>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleSaveNewSequence("COOL_DOWN")}
                          disabled={
                            !isNewSequenceFormValid() ||
                            addSequenceMutation.isPending
                          }
                        >
                          <CheckIcon className="h-4 w-4 mr-2" />
                          Add Sequence
                        </Button>
                        <Button
                          variant="outline"
                          onClick={handleCancelAddSequence}
                          disabled={addSequenceMutation.isPending}
                        >
                          <XIcon className="h-4 w-4 mr-2" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Button
                  variant="outline"
                  onClick={() => handleAddSequenceClick("COOL_DOWN")}
                  className="w-full"
                >
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Add Exercise Sequence
                </Button>
              )}
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
