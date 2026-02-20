"use client";

import * as React from "react";
import {
  Card,
  CardDescription,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  PencilIcon,
  TrashIcon,
  CheckIcon,
  XIcon,
  PlusIcon,
} from "lucide-react";
import type {
  ExerciseSequence,
  Exercise,
  ExerciseVariant,
} from "@/lib/apiClient/types.gen";
import { formatEnumMember } from "@/lib/utils";
import { useUpdateExerciseSet } from "@/hooks/mutations/useUpdateExerciseSet";
import { useDeleteExerciseSet } from "@/hooks/mutations/useDeleteExerciseSet";
import { useAddExerciseSet } from "@/hooks/mutations/useAddExerciseSet";
import { ExerciseSelector } from "@/components/exercise-selector";

interface ExerciseSequenceCardProps {
  sequence: ExerciseSequence;
}

export function ExerciseSequenceCard({ sequence }: ExerciseSequenceCardProps) {
  const [editingSetId, setEditingSetId] = React.useState<number | null>(null);
  const [addingSet, setAddingSet] = React.useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [setToDelete, setSetToDelete] = React.useState<number | null>(null);

  const [formData, setFormData] = React.useState<{
    exerciseId: number | null;
    exercise: Exercise | null;
    variant: ExerciseVariant | "";
    reps: number;
    durationSeconds: number;
  }>({
    exerciseId: null,
    exercise: null,
    variant: "",
    reps: 0,
    durationSeconds: 0,
  });

  const updateMutation = useUpdateExerciseSet();
  const deleteMutation = useDeleteExerciseSet();
  const addMutation = useAddExerciseSet();

  const handleEditClick = (setId: number) => {
    const set = sequence.sets.find((s) => s.id === setId);
    if (set) {
      setFormData({
        exerciseId: set.exercise.id,
        exercise: set.exercise,
        variant: set.variant,
        reps: set.reps,
        durationSeconds: set.duration_seconds,
      });
      setEditingSetId(setId);
    }
  };

  const handleCancelEdit = () => {
    setEditingSetId(null);
    setFormData({
      exerciseId: null,
      exercise: null,
      variant: "",
      reps: 0,
      durationSeconds: 0,
    });
  };

  const handleSaveEdit = async (setId: number) => {
    if (!formData.variant) return;

    try {
      await updateMutation.mutateAsync({
        sequenceId: sequence.id,
        setId,
        reps: formData.reps,
        durationSeconds: formData.durationSeconds,
        variant: formData.variant as ExerciseVariant,
      });
      setEditingSetId(null);
    } catch (error) {
      // Error handled by mutation
    }
  };

  const handleDeleteClick = (setId: number) => {
    setSetToDelete(setId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (setToDelete) {
      try {
        await deleteMutation.mutateAsync({
          sequenceId: sequence.id,
          setId: setToDelete,
        });
        setDeleteDialogOpen(false);
        setSetToDelete(null);
      } catch (error) {
        // Error handled by mutation
      }
    }
  };

  const handleAddClick = () => {
    setFormData({
      exerciseId: null,
      exercise: null,
      variant: "",
      reps: 0,
      durationSeconds: 0,
    });
    setAddingSet(true);
  };

  const handleCancelAdd = () => {
    setAddingSet(false);
    setFormData({
      exerciseId: null,
      exercise: null,
      variant: "",
      reps: 0,
      durationSeconds: 0,
    });
  };

  const handleSaveAdd = async () => {
    if (
      formData.exerciseId &&
      formData.variant &&
      formData.reps > 0 &&
      formData.durationSeconds > 0
    ) {
      try {
        await addMutation.mutateAsync({
          sequenceId: sequence.id,
          exerciseId: formData.exerciseId,
          reps: formData.reps,
          durationSeconds: formData.durationSeconds,
          variant: formData.variant as ExerciseVariant,
        });
        setAddingSet(false);
        setFormData({
          exerciseId: null,
          exercise: null,
          variant: "",
          reps: 0,
          durationSeconds: 0,
        });
      } catch (error) {
        // Error handled by mutation
      }
    }
  };

  const isFormValid = () => {
    if (editingSetId !== null) {
      return (
        formData.reps > 0 && formData.durationSeconds > 0 && formData.variant
      );
    }
    return (
      formData.exerciseId !== null &&
      formData.reps > 0 &&
      formData.durationSeconds > 0 &&
      formData.variant
    );
  };

  return (
    <>
      <Card className="transition-all duration-200 hover:shadow-lg hover:-translate-y-1 border-2">
        <CardHeader className="pb-3">
          <CardTitle className="text-xl">{sequence.name}</CardTitle>
          <CardDescription>
            <p>
              Total duration: {getSequenceDurationSeconds(sequence)}s, Reps:{" "}
              {sequence.reps}
            </p>
            <p>{sequence.notes}</p>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="font-semibold">Exercise</TableHead>
                <TableHead className="font-semibold">Variant</TableHead>
                <TableHead className="font-semibold">Reps</TableHead>
                <TableHead className="font-semibold">Duration</TableHead>
                <TableHead className="font-semibold">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sequence.sets.map((set) => (
                <TableRow key={set.id}>
                  {editingSetId === set.id ? (
                    <>
                      <TableCell className="font-medium">
                        {set.exercise.name}
                      </TableCell>
                      <TableCell>
                        <Select
                          value={formData.variant}
                          onValueChange={(value) =>
                            setFormData({
                              ...formData,
                              variant: value as ExerciseVariant,
                            })
                          }
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {set.exercise.variants.map((variant) => (
                              <SelectItem key={variant} value={variant}>
                                {formatEnumMember(variant)}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={formData.reps}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              reps: Number(e.target.value),
                            })
                          }
                          className="w-20"
                          min="1"
                        />
                      </TableCell>
                      <TableCell>
                        <Input
                          type="number"
                          value={formData.durationSeconds}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              durationSeconds: Number(e.target.value),
                            })
                          }
                          className="w-20"
                          min="1"
                        />
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="icon-sm"
                            variant="ghost"
                            onClick={() => handleSaveEdit(set.id)}
                            disabled={
                              !isFormValid() || updateMutation.isPending
                            }
                          >
                            <CheckIcon className="h-4 w-4" />
                          </Button>
                          <Button
                            size="icon-sm"
                            variant="ghost"
                            onClick={handleCancelEdit}
                            disabled={updateMutation.isPending}
                          >
                            <XIcon className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </>
                  ) : (
                    <>
                      <TableCell className="font-medium">
                        {set.exercise.name}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {formatEnumMember(set.variant)}
                        </Badge>
                      </TableCell>
                      <TableCell>{set.reps || "-"}</TableCell>
                      <TableCell>
                        {set.duration_seconds
                          ? `${set.duration_seconds}s`
                          : "-"}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="icon-sm"
                            variant="ghost"
                            onClick={() => handleEditClick(set.id)}
                          >
                            <PencilIcon className="h-4 w-4" />
                          </Button>
                          <Button
                            size="icon-sm"
                            variant="ghost"
                            onClick={() => handleDeleteClick(set.id)}
                          >
                            <TrashIcon className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </>
                  )}
                </TableRow>
              ))}
              {addingSet && (
                <TableRow>
                  <TableCell>
                    <ExerciseSelector
                      value={formData.exerciseId}
                      onChange={(exerciseId, exercise) =>
                        setFormData({
                          ...formData,
                          exerciseId,
                          exercise,
                          variant: exercise.variants[0] || "",
                        })
                      }
                    />
                  </TableCell>
                  <TableCell>
                    {formData.exercise && (
                      <Select
                        value={formData.variant}
                        onValueChange={(value) =>
                          setFormData({
                            ...formData,
                            variant: value as ExerciseVariant,
                          })
                        }
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {formData.exercise.variants.map((variant) => (
                            <SelectItem key={variant} value={variant}>
                              {formatEnumMember(variant)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    )}
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={formData.reps}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          reps: Number(e.target.value),
                        })
                      }
                      className="w-20"
                      min="1"
                      placeholder="Reps"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      value={formData.durationSeconds}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          durationSeconds: Number(e.target.value),
                        })
                      }
                      className="w-20"
                      min="1"
                      placeholder="Seconds"
                    />
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="icon-sm"
                        variant="ghost"
                        onClick={handleSaveAdd}
                        disabled={!isFormValid() || addMutation.isPending}
                      >
                        <CheckIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        size="icon-sm"
                        variant="ghost"
                        onClick={handleCancelAdd}
                        disabled={addMutation.isPending}
                      >
                        <XIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
          {!addingSet && (
            <div className="mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={handleAddClick}
                className="w-full"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Add Set
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Set</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this set? This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              disabled={deleteMutation.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

function getSequenceDurationSeconds(sequence: ExerciseSequence): number {
  let total_duration_seconds = 0;
  for (let i = 0; i < sequence.sets.length; i++) {
    total_duration_seconds += sequence.sets[i].duration_seconds;
  }

  return total_duration_seconds * sequence.reps;
}
