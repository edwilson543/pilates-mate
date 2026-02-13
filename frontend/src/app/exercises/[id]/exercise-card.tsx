import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Exercise } from "@/lib/apiClient/types.gen";

import {formatEnumMember} from "@/lib/utils";
interface ExerciseCardProps {
  exercise: Exercise;
}

export function ExerciseCard({ exercise }: ExerciseCardProps) {
  return (
    <Card className="transition-all duration-200 hover:shadow-lg hover:-translate-y-1 border-2">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">{exercise.name}</CardTitle>
          <Badge
            variant={
              exercise.difficulty === "BEGINNER"
                ? "secondary"
                : exercise.difficulty === "INTERMEDIATE"
                  ? "default"
                  : "destructive"
            }
            className="px-3 py-1"
          >
            {formatEnumMember(exercise.difficulty)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground leading-relaxed">
            {exercise.description}
          </p>
          <div className="flex gap-6 text-sm pt-2">
            <div className="flex-1">
              <span className="font-semibold text-foreground">
                Muscle Group:
              </span>{" "}
              <span className="text-muted-foreground">
                {formatEnumMember(exercise.primary_muscle_group)}
              </span>
            </div>
            <div className="flex-1">
              <span className="font-semibold text-foreground">
                Starting Position:
              </span>{" "}
              <span className="text-muted-foreground">
                {formatEnumMember(exercise.starting_position)}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
