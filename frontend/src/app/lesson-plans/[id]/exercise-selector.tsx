"use client";

import * as React from "react";
import { useExercises } from "@/hooks/queries/useExercises";
import type { Exercise } from "@/lib/apiClient";
import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
} from "@/components/ui/combobox";

interface ExerciseSelectorProps {
  value: number | null;
  onChange: (exerciseId: number | null, exercise: Exercise | null) => void;
}

export function ExerciseSelector({ value, onChange }: ExerciseSelectorProps) {
  const { data: exercises = [], isLoading } = useExercises();
  const [inputValue, setInputValue] = React.useState("");

  const selectedExercise = exercises.find((ex) => ex.id === value);

  // Update input value when a new exercise is selected from outside
  React.useEffect(() => {
    if (selectedExercise && inputValue !== selectedExercise.name) {
      setInputValue(selectedExercise.name);
    } else if (!selectedExercise && inputValue !== "") {
      setInputValue("");
    }
  }, [selectedExercise, inputValue]);

  const filteredExercises = exercises.filter((exercise) =>
    exercise.name.toLowerCase().includes(inputValue.toLowerCase()),
  );

  return (
    <Combobox
      value={value !== null ? String(value) : ""}
      onValueChange={(newValue: string) => {
        if (!newValue) {
          // Handle clear
          setInputValue("");
          onChange(null, null);
        } else {
          // Handle selection
          const exerciseId = Number(newValue);
          const exercise = exercises.find((ex) => ex.id === exerciseId);
          if (exercise) {
            setInputValue(exercise.name);
            onChange(exerciseId, exercise);
          }
        }
      }}
    >
      <ComboboxInput
        placeholder={isLoading ? "Loading..." : "Select exercise..."}
        value={inputValue}
        onInput={(e) => setInputValue(e.currentTarget.value)}
        showClear
        disabled={isLoading}
      />
      <ComboboxContent>
        <ComboboxList>
          <ComboboxEmpty>No exercises found</ComboboxEmpty>
          {filteredExercises.map((exercise) => (
            <ComboboxItem key={exercise.id} value={String(exercise.id)}>
              {exercise.name}
            </ComboboxItem>
          ))}
        </ComboboxList>
      </ComboboxContent>
    </Combobox>
  );
}
