"use client";

import { PageHeader } from "@/components/common/page-header";
import { useExercises } from "@/hooks/queries/useExercises";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { formatEnumMember } from "@/lib/utils";

export default function ExercisesPage() {
  const router = useRouter();
  const { data: exercises, isLoading, error } = useExercises();

  if (isLoading) {
    return (
      <div className="p-8">
        <PageHeader title="Exercises" />
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <PageHeader title="Exercises" />
        <div className="text-center py-12">
          <p className="text-destructive">Failed to load exercises</p>
        </div>
      </div>
    );
  }

  if (!exercises || exercises.length === 0) {
    return (
      <div className="p-8">
        <PageHeader title="Exercises" />
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">
            No exercises found. Create your first exercise to get started.
          </p>
          <Button onClick={() => router.push("/exercises/new")}>
            Create Exercise
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Exercises"
        actionButton={{
          label: "Create Exercise",
          onClick: () => router.push("/exercises/new"),
        }}
      />
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Difficulty</TableHead>
              <TableHead>Muscle Group</TableHead>
              <TableHead>Starting Position</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {exercises.map((exercise) => (
              <TableRow
                key={exercise.id}
                className="cursor-pointer"
                onClick={() => router.push(`/exercises/${exercise.id}`)}
              >
                <TableCell className="font-medium">{exercise.name}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      exercise.difficulty === "BEGINNER"
                        ? "secondary"
                        : exercise.difficulty === "INTERMEDIATE"
                          ? "default"
                          : "destructive"
                    }
                  >
                    {formatEnumMember(exercise.difficulty)}
                  </Badge>
                </TableCell>
                <TableCell>
                  {formatEnumMember(exercise.primary_muscle_group)}
                </TableCell>
                <TableCell>
                  {formatEnumMember(exercise.starting_position)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
