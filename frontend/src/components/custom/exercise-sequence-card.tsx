import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { ExerciseSequence } from "@/lib/apiClient/types.gen";

interface ExerciseSequenceCardProps {
  sequence: ExerciseSequence;
  index: number;
}

export function ExerciseSequenceCard({
  sequence,
  index,
}: ExerciseSequenceCardProps) {
  return (
    <Card className="transition-all duration-200 hover:shadow-lg hover:-translate-y-1 border-2">
      <CardHeader className="pb-3">
        <CardTitle className="text-xl">Sequence {index + 1}</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="font-semibold">Exercise</TableHead>
              <TableHead className="font-semibold">Reps</TableHead>
              <TableHead className="font-semibold">Duration</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sequence.sets.map((set, setIndex) => (
              <TableRow key={setIndex}>
                <TableCell className="font-medium">
                  {set.exercise.name}
                </TableCell>
                <TableCell>{set.reps || "-"}</TableCell>
                <TableCell>
                  {set.duration_seconds ? `${set.duration_seconds}s` : "-"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        {sequence.notes && (
          <div className="mt-4 p-4 bg-muted/50 rounded-lg border">
            <p className="text-sm leading-relaxed">
              <span className="font-semibold">Notes:</span> {sequence.notes}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
