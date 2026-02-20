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
import {
  Pencil,
  Search,
  X,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import { useState, useMemo } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Combobox,
  ComboboxChips,
  ComboboxChip,
  ComboboxChipsInput,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxItem,
  ComboboxList,
  useComboboxAnchor,
} from "@/components/ui/combobox";
import { Label } from "@/components/ui/label";

const difficultyOptions = [
  { value: "BEGINNER", label: "Beginner" },
  { value: "INTERMEDIATE", label: "Intermediate" },
  { value: "ADVANCED", label: "Advanced" },
] as const;

const muscleGroupOptions = [
  { value: "CORE", label: "Core" },
  { value: "GLUTES", label: "Glutes" },
  { value: "HIP_FLEXORS", label: "Hip Flexors" },
  { value: "BACK_EXTENSORS", label: "Back Extensors" },
  { value: "SHOULDERS", label: "Shoulders" },
  { value: "INNER_THIGHS", label: "Inner Thighs" },
  { value: "HAMSTRINGS", label: "Hamstrings" },
  { value: "OBLIQUES", label: "Obliques" },
  { value: "TRICEPS", label: "Triceps" },
  { value: "CHEST", label: "Chest" },
] as const;

const startingPositionOptions = [
  { value: "SUPINE", label: "Supine" },
  { value: "PRONE", label: "Prone" },
  { value: "SIDE_LYING", label: "Side Lying" },
  { value: "SEATED", label: "Seated" },
  { value: "QUADRUPED", label: "Quadruped" },
  { value: "STANDING", label: "Standing" },
  { value: "KNEELING", label: "Kneeling" },
  { value: "PLANK", label: "Plank" },
  { value: "SIDE_KNEELING", label: "Side Kneeling" },
] as const;

export default function ExercisesPage() {
  const router = useRouter();
  const { data: exercises, isLoading, error } = useExercises();

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDifficulties, setSelectedDifficulties] = useState<string[]>(
    [],
  );
  const [selectedMuscleGroups, setSelectedMuscleGroups] = useState<string[]>(
    [],
  );
  const [selectedStartingPositions, setSelectedStartingPositions] = useState<
    string[]
  >([]);
  const [sortColumn, setSortColumn] = useState<
    "name" | "difficulty" | "primary_muscle_group"
  >("name");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const difficultyAnchor = useComboboxAnchor();
  const muscleGroupAnchor = useComboboxAnchor();
  const startingPositionAnchor = useComboboxAnchor();

  const filteredAndSortedExercises = useMemo(() => {
    if (!exercises) return [];

    let result = exercises;

    // Apply search filter
    if (searchTerm) {
      result = result.filter((ex) =>
        ex.name.toLowerCase().includes(searchTerm.toLowerCase()),
      );
    }

    // Apply difficulty filter
    if (selectedDifficulties.length > 0) {
      result = result.filter((ex) =>
        selectedDifficulties.includes(ex.difficulty),
      );
    }

    // Apply muscle group filter
    if (selectedMuscleGroups.length > 0) {
      result = result.filter((ex) =>
        selectedMuscleGroups.includes(ex.primary_muscle_group),
      );
    }

    // Apply starting position filter
    if (selectedStartingPositions.length > 0) {
      result = result.filter((ex) =>
        selectedStartingPositions.includes(ex.starting_position),
      );
    }

    // Apply sorting
    result = [...result].sort((a, b) => {
      let comparison = 0;

      switch (sortColumn) {
        case "name":
          comparison = a.name.localeCompare(b.name);
          break;
        case "difficulty": {
          const difficultyOrder = {
            BEGINNER: 0,
            INTERMEDIATE: 1,
            ADVANCED: 2,
          };
          comparison =
            difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
          break;
        }
        case "primary_muscle_group":
          comparison = a.primary_muscle_group.localeCompare(
            b.primary_muscle_group,
          );
          break;
      }

      return sortDirection === "asc" ? comparison : -comparison;
    });

    return result;
  }, [
    exercises,
    searchTerm,
    selectedDifficulties,
    selectedMuscleGroups,
    selectedStartingPositions,
    sortColumn,
    sortDirection,
  ]);

  const hasActiveFilters =
    searchTerm ||
    selectedDifficulties.length > 0 ||
    selectedMuscleGroups.length > 0 ||
    selectedStartingPositions.length > 0;

  const handleSort = (
    column: "name" | "difficulty" | "primary_muscle_group",
  ) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  const clearFilters = () => {
    setSearchTerm("");
    setSelectedDifficulties([]);
    setSelectedMuscleGroups([]);
    setSelectedStartingPositions([]);
  };

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

  const hasNoExercises = !exercises || exercises.length === 0;
  const hasNoFilteredResults =
    !hasNoExercises && filteredAndSortedExercises.length === 0;

  if (hasNoExercises) {
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

      {/* Filter Controls */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="space-y-4">
            {/* Search Input */}
            <div>
              <Label className="text-sm font-medium mb-2 block">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search exercises..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            {/* Difficulty Filter */}
            <div>
              <Label className="text-sm font-medium mb-2 block">
                Difficulty
              </Label>
              <Combobox
                value={selectedDifficulties}
                onValueChange={setSelectedDifficulties}
                multiple
              >
                <ComboboxChips ref={difficultyAnchor}>
                  {selectedDifficulties.map((value) => {
                    const option = difficultyOptions.find(
                      (o) => o.value === value,
                    );
                    return (
                      <ComboboxChip key={value}>
                        {option?.label || value}
                      </ComboboxChip>
                    );
                  })}
                  <ComboboxChipsInput
                    placeholder={
                      selectedDifficulties.length === 0
                        ? "Select difficulty levels..."
                        : undefined
                    }
                  />
                </ComboboxChips>
                <ComboboxContent anchor={difficultyAnchor}>
                  <ComboboxList>
                    {difficultyOptions
                      .filter((o) => !selectedDifficulties.includes(o.value))
                      .map((option) => (
                        <ComboboxItem key={option.value} value={option.value}>
                          {option.label}
                        </ComboboxItem>
                      ))}
                    {selectedDifficulties.length ===
                      difficultyOptions.length && (
                      <ComboboxEmpty>All difficulties selected</ComboboxEmpty>
                    )}
                  </ComboboxList>
                </ComboboxContent>
              </Combobox>
            </div>

            {/* Muscle Group Filter */}
            <div>
              <Label className="text-sm font-medium mb-2 block">
                Muscle Group
              </Label>
              <Combobox
                value={selectedMuscleGroups}
                onValueChange={setSelectedMuscleGroups}
                multiple
              >
                <ComboboxChips ref={muscleGroupAnchor}>
                  {selectedMuscleGroups.map((value) => {
                    const option = muscleGroupOptions.find(
                      (o) => o.value === value,
                    );
                    return (
                      <ComboboxChip key={value}>
                        {option?.label || value}
                      </ComboboxChip>
                    );
                  })}
                  <ComboboxChipsInput
                    placeholder={
                      selectedMuscleGroups.length === 0
                        ? "Select muscle groups..."
                        : undefined
                    }
                  />
                </ComboboxChips>
                <ComboboxContent anchor={muscleGroupAnchor}>
                  <ComboboxList>
                    {muscleGroupOptions
                      .filter((o) => !selectedMuscleGroups.includes(o.value))
                      .map((option) => (
                        <ComboboxItem key={option.value} value={option.value}>
                          {option.label}
                        </ComboboxItem>
                      ))}
                    {selectedMuscleGroups.length ===
                      muscleGroupOptions.length && (
                      <ComboboxEmpty>All muscle groups selected</ComboboxEmpty>
                    )}
                  </ComboboxList>
                </ComboboxContent>
              </Combobox>
            </div>

            {/* Starting Position Filter */}
            <div>
              <Label className="text-sm font-medium mb-2 block">
                Starting Position
              </Label>
              <Combobox
                value={selectedStartingPositions}
                onValueChange={setSelectedStartingPositions}
                multiple
              >
                <ComboboxChips ref={startingPositionAnchor}>
                  {selectedStartingPositions.map((value) => {
                    const option = startingPositionOptions.find(
                      (o) => o.value === value,
                    );
                    return (
                      <ComboboxChip key={value}>
                        {option?.label || value}
                      </ComboboxChip>
                    );
                  })}
                  <ComboboxChipsInput
                    placeholder={
                      selectedStartingPositions.length === 0
                        ? "Select starting positions..."
                        : undefined
                    }
                  />
                </ComboboxChips>
                <ComboboxContent anchor={startingPositionAnchor}>
                  <ComboboxList>
                    {startingPositionOptions
                      .filter(
                        (o) => !selectedStartingPositions.includes(o.value),
                      )
                      .map((option) => (
                        <ComboboxItem key={option.value} value={option.value}>
                          {option.label}
                        </ComboboxItem>
                      ))}
                    {selectedStartingPositions.length ===
                      startingPositionOptions.length && (
                      <ComboboxEmpty>
                        All starting positions selected
                      </ComboboxEmpty>
                    )}
                  </ComboboxList>
                </ComboboxContent>
              </Combobox>
            </div>

            {/* Clear Filters Button */}
            {hasActiveFilters && (
              <div className="flex justify-end">
                <Button variant="ghost" onClick={clearFilters}>
                  <X className="h-4 w-4 mr-2" />
                  Clear Filters
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Filter Results Indicator */}
      {hasActiveFilters && (
        <div className="mb-4 text-sm text-muted-foreground">
          Showing {filteredAndSortedExercises.length} of {exercises.length}{" "}
          exercises
        </div>
      )}

      {/* Empty State for Filtered Results */}
      {hasNoFilteredResults ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">
            No exercises match your filters. Try adjusting your search criteria.
          </p>
          <Button variant="outline" onClick={clearFilters}>
            <X className="h-4 w-4 mr-2" />
            Clear Filters
          </Button>
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort("name")}
                    className="h-auto p-0 font-semibold hover:bg-transparent"
                  >
                    Name
                    {sortColumn === "name" &&
                      (sortDirection === "asc" ? (
                        <ArrowUp className="ml-2 h-4 w-4" />
                      ) : (
                        <ArrowDown className="ml-2 h-4 w-4" />
                      ))}
                    {sortColumn !== "name" && (
                      <ArrowUpDown className="ml-2 h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort("difficulty")}
                    className="h-auto p-0 font-semibold hover:bg-transparent"
                  >
                    Difficulty
                    {sortColumn === "difficulty" &&
                      (sortDirection === "asc" ? (
                        <ArrowUp className="ml-2 h-4 w-4" />
                      ) : (
                        <ArrowDown className="ml-2 h-4 w-4" />
                      ))}
                    {sortColumn !== "difficulty" && (
                      <ArrowUpDown className="ml-2 h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </TableHead>
                <TableHead>
                  <Button
                    variant="ghost"
                    onClick={() => handleSort("primary_muscle_group")}
                    className="h-auto p-0 font-semibold hover:bg-transparent"
                  >
                    Muscle Group
                    {sortColumn === "primary_muscle_group" &&
                      (sortDirection === "asc" ? (
                        <ArrowUp className="ml-2 h-4 w-4" />
                      ) : (
                        <ArrowDown className="ml-2 h-4 w-4" />
                      ))}
                    {sortColumn !== "primary_muscle_group" && (
                      <ArrowUpDown className="ml-2 h-4 w-4 text-muted-foreground" />
                    )}
                  </Button>
                </TableHead>
                <TableHead>Starting Position</TableHead>
                <TableHead className="w-[80px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedExercises.map((exercise) => (
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
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/exercises/${exercise.id}/edit`);
                      }}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
