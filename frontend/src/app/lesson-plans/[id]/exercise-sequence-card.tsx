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
import type { ExerciseSequence } from "@/lib/apiClient/types.gen";

interface ExerciseSequenceCardProps {
  sequence: ExerciseSequence;
}

export function ExerciseSequenceCard({ sequence }: ExerciseSequenceCardProps) {
  return (
    <Card className="transition-all duration-200 hover:shadow-lg hover:-translate-y-1 border-2">
      <CardHeader className="pb-3">
        <CardTitle className="text-xl">{sequence.name}</CardTitle>
        <CardDescription>
            <p>Total duration: {getSequenceDurationSeconds(sequence)}s, Reps: {sequence.reps}</p>
            <p>{sequence.notes}</p>
        </CardDescription>
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
      </CardContent>
    </Card>
  );
}

function getSequenceDurationSeconds(sequence: ExerciseSequence): number {
    let total_duration_seconds = 0;
    for (let i = 0; i < sequence.sets.length; i++) {
      total_duration_seconds += sequence.sets[i].duration_seconds;
    }

    return total_duration_seconds * sequence.reps
}