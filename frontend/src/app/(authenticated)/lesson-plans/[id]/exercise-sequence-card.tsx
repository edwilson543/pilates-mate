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
  MovementVariant,
  Equipment,
} from "@/lib/apiClient/types.gen";
import { formatEnumMember } from "@/lib/utils";
import { useUpdateExerciseSet } from "@/hooks/mutations/useUpdateExerciseSet";
import { useDeleteExerciseSet } from "@/hooks/mutations/useDeleteExerciseSet";
import { useAddExerciseSet } from "@/hooks/mutations/useAddExerciseSet";
import { useUpdateExerciseSequence } from "@/hooks/mutations/useUpdateExerciseSequence";
import { useDeleteExerciseSequence } from "@/hooks/mutations/useDeleteExerciseSequence";
import { ExerciseSelector } from "@/app/(authenticated)/lesson-plans/[id]/exercise-selector";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface ExerciseSequenceCardProps {
  sequence: ExerciseSequence;
}

export function ExerciseSequenceCard({ sequence }: ExerciseSequenceCardProps) {
  const [editingSetId, setEditingSetId] = React.useState<number | null>(null);
  const [addingSet, setAddingSet] = React.useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
  const [setToDelete, setSetToDelete] = React.useState<number | null>(null);
  const [editingSequence, setEditingSequence] = React.useState(false);
  const [deleteSequenceDialogOpen, setDeleteSequenceDialogOpen] =
    React.useState(false);
  const [sequenceFormData, setSequenceFormData] = React.useState({
    name: "",
    reps: 0,
    notes: "",
  });

  const [formData, setFormData] = React.useState<{
    exerciseId: number | null;
    exercise: Exercise | null;
    movement_variant: MovementVariant | "";
    equipment_variant: Equipment[];
    reps: number;
    durationSeconds: number;
  }>({
    exerciseId: null,
    exercise: null,
    movement_variant: "",
    equipment_variant: [],
    reps: 0,
    durationSeconds: 0,
  });

  const updateMutation = useUpdateExerciseSet();
  const deleteMutation = useDeleteExerciseSet();
  const addMutation = useAddExerciseSet();
  const updateSequenceMutation = useUpdateExerciseSequence();
  const deleteSequenceMutation = useDeleteExerciseSequence();

  const handleEditClick = (setId: number) => {
    const set = sequence.sets.find((s) => s.id === setId);
    if (set) {
      setFormData({
        exerciseId: set.exercise.id,
        exercise: set.exercise,
        movement_variant: set.movement_variant,
        equipment_variant: set.equipment_variant,
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
      movement_variant: "",
      equipment_variant: [],
      reps: 0,
      durationSeconds: 0,
    });
  };

  const handleSaveEdit = async (setId: number) => {
    if (!formData.movement_variant) return;

    try {
      await updateMutation.mutateAsync({
        sequenceId: sequence.id,
        setId,
        reps: formData.reps,
        durationSeconds: formData.durationSeconds,
        movement_variant: formData.movement_variant as MovementVariant,
        equipment_variant: formData.equipment_variant,
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
      movement_variant: "",
      equipment_variant: [],
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
      movement_variant: "",
      equipment_variant: [],
      reps: 0,
      durationSeconds: 0,
    });
  };

  const handleSaveAdd = async () => {
    if (
      formData.exerciseId &&
      formData.movement_variant &&
      formData.reps > 0 &&
      formData.durationSeconds > 0
    ) {
      try {
        await addMutation.mutateAsync({
          sequenceId: sequence.id,
          exerciseId: formData.exerciseId,
          reps: formData.reps,
          durationSeconds: formData.durationSeconds,
          movement_variant: formData.movement_variant as MovementVariant,
          equipment_variant: formData.equipment_variant,
        });
        setAddingSet(false);
        setFormData({
          exerciseId: null,
          exercise: null,
          movement_variant: "",
          equipment_variant: [],
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
        formData.reps > 0 &&
        formData.durationSeconds > 0 &&
        formData.movement_variant
      );
    }
    return (
      formData.exerciseId !== null &&
      formData.reps > 0 &&
      formData.durationSeconds > 0 &&
      formData.movement_variant
    );
  };

  const handleEditSequenceClick = () => {
    setSequenceFormData({
      name: sequence.name,
      reps: sequence.reps,
      notes: sequence.notes,
    });
    setEditingSequence(true);
  };

  const handleCancelSequenceEdit = () => {
    setEditingSequence(false);
    setSequenceFormData({
      name: "",
      reps: 0,
      notes: "",
    });
  };

  const handleSaveSequenceEdit = async () => {
    if (sequenceFormData.name && sequenceFormData.reps > 0) {
      try {
        await updateSequenceMutation.mutateAsync({
          sequenceId: sequence.id,
          name: sequenceFormData.name,
          reps: sequenceFormData.reps,
          notes: sequenceFormData.notes,
        });
        setEditingSequence(false);
      } catch (error) {
        // Error handled by mutation
      }
    }
  };

  const handleDeleteSequenceClick = () => {
    setDeleteSequenceDialogOpen(true);
  };

  const handleConfirmDeleteSequence = async () => {
    try {
      await deleteSequenceMutation.mutateAsync({
        sequenceId: sequence.id,
      });
      setDeleteSequenceDialogOpen(false);
    } catch (error) {
      // Error handled by mutation
    }
  };

  const isSequenceFormValid = () => {
    return sequenceFormData.name.length > 0 && sequenceFormData.reps > 0;
  };

  return (
    <>
      <Card className="transition-shadow duration-200 hover:shadow-lg border-2">
        <CardHeader className="pb-3">
          {editingSequence ? (
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div className="flex-1 space-y-4">
                  <div>
                    <Label htmlFor="sequence-name">Sequence Name</Label>
                    <Input
                      id="sequence-name"
                      value={sequenceFormData.name}
                      onChange={(e) =>
                        setSequenceFormData({
                          ...sequenceFormData,
                          name: e.target.value,
                        })
                      }
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="sequence-reps">Reps</Label>
                    <Input
                      id="sequence-reps"
                      type="number"
                      value={sequenceFormData.reps}
                      onChange={(e) =>
                        setSequenceFormData({
                          ...sequenceFormData,
                          reps: Number(e.target.value),
                        })
                      }
                      className="mt-1 w-32"
                      min="1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="sequence-notes">Notes</Label>
                    <Textarea
                      id="sequence-notes"
                      value={sequenceFormData.notes}
                      onChange={(e) =>
                        setSequenceFormData({
                          ...sequenceFormData,
                          notes: e.target.value,
                        })
                      }
                      className="mt-1"
                    />
                  </div>
                </div>
                <div className="flex gap-2 ml-4">
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={handleSaveSequenceEdit}
                    disabled={
                      !isSequenceFormValid() || updateSequenceMutation.isPending
                    }
                  >
                    <CheckIcon className="h-4 w-4" />
                  </Button>
                  <Button
                    size="icon-sm"
                    variant="ghost"
                    onClick={handleCancelSequenceEdit}
                    disabled={updateSequenceMutation.isPending}
                  >
                    <XIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-xl">{sequence.name}</CardTitle>
                <CardDescription>
                  <p>
                    Total duration: {getSequenceDurationSeconds(sequence)}s,
                    Reps: {sequence.reps}
                  </p>
                  <p>{sequence.notes}</p>
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  size="icon-sm"
                  variant="ghost"
                  onClick={handleEditSequenceClick}
                >
                  <PencilIcon className="h-4 w-4" />
                </Button>
                <Button
                  size="icon-sm"
                  variant="ghost"
                  onClick={handleDeleteSequenceClick}
                >
                  <TrashIcon className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            </div>
          )}
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="font-semibold w-48">Exercise</TableHead>
                <TableHead className="font-semibold w-32">Movement</TableHead>
                <TableHead className="font-semibold w-32">Equipment</TableHead>
                <TableHead className="font-semibold w-20">Reps</TableHead>
                <TableHead className="font-semibold w-24">Duration</TableHead>
                <TableHead className="font-semibold w-28">Actions</TableHead>
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
                          value={formData.movement_variant}
                          onValueChange={(value) =>
                            setFormData({
                              ...formData,
                              movement_variant: value as MovementVariant,
                            })
                          }
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {set.exercise.movement_variants.map(
                              (movement_variant) => (
                                <SelectItem
                                  key={movement_variant}
                                  value={movement_variant}
                                >
                                  {formatEnumMember(movement_variant)}
                                </SelectItem>
                              ),
                            )}
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell>
                        <Select
                          value={formData.equipment_variant[0] || "NONE"}
                          onValueChange={(value) =>
                            setFormData({
                              ...formData,
                              equipment_variant:
                                value === "NONE" ? [] : [value as Equipment],
                            })
                          }
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue placeholder="None" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="NONE">None</SelectItem>
                            {set.exercise.equipment_variants.map(
                              (equipment) => (
                                <SelectItem key={equipment} value={equipment}>
                                  {formatEnumMember(equipment)}
                                </SelectItem>
                              ),
                            )}
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
                          {formatEnumMember(set.movement_variant)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {set.equipment_variant.length > 0 ? (
                          <div className="flex gap-1 flex-wrap">
                            {set.equipment_variant.map((equipment) => (
                              <Badge
                                key={equipment}
                                variant="outline"
                                className="text-xs"
                              >
                                {formatEnumMember(equipment)}
                              </Badge>
                            ))}
                          </div>
                        ) : (
                          "-"
                        )}
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
                          movement_variant:
                            exercise?.movement_variants[0] || "",
                          equipment_variant: [],
                        })
                      }
                    />
                  </TableCell>
                  <TableCell>
                    {formData.exercise && (
                      <Select
                        value={formData.movement_variant}
                        onValueChange={(value) =>
                          setFormData({
                            ...formData,
                            movement_variant: value as MovementVariant,
                          })
                        }
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {formData.exercise.movement_variants.map(
                            (movement_variant) => (
                              <SelectItem
                                key={movement_variant}
                                value={movement_variant}
                              >
                                {formatEnumMember(movement_variant)}
                              </SelectItem>
                            ),
                          )}
                        </SelectContent>
                      </Select>
                    )}
                  </TableCell>
                  <TableCell>
                    {formData.exercise && (
                      <Select
                        value={formData.equipment_variant[0] || "NONE"}
                        onValueChange={(value) =>
                          setFormData({
                            ...formData,
                            equipment_variant:
                              value === "NONE" ? [] : [value as Equipment],
                          })
                        }
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue placeholder="None" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="NONE">None</SelectItem>
                          {formData.exercise.equipment_variants.map(
                            (equipment) => (
                              <SelectItem key={equipment} value={equipment}>
                                {formatEnumMember(equipment)}
                              </SelectItem>
                            ),
                          )}
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

      <AlertDialog
        open={deleteSequenceDialogOpen}
        onOpenChange={setDeleteSequenceDialogOpen}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Exercise Sequence</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this sequence? This will delete
              all sets within the sequence. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDeleteSequence}
              disabled={deleteSequenceMutation.isPending}
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
