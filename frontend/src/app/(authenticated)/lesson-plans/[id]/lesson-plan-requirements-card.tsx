import type { LessonPlanRequirements } from "@/lib/apiClient/types.gen";

function formatEnum(value: string): string {
  return value
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/^\w/, (c) => c.toUpperCase());
}

export function LessonPlanRequirementsTable({
  requirements,
}: {
  requirements: LessonPlanRequirements;
}) {
  return (
    <table className="w-full text-sm">
      <tbody>
        <tr>
          <td className="py-1 pr-4 text-muted-foreground font-medium">
            Duration
          </td>
          <td className="py-1">{requirements.duration_minutes} min</td>
        </tr>
        <tr>
          <td className="py-1 pr-4 text-muted-foreground font-medium">
            Difficulty
          </td>
          <td className="py-1">
            {formatEnum(requirements.target_difficulty)}
          </td>
        </tr>
        <tr>
          <td className="py-1 pr-4 text-muted-foreground font-medium">
            Muscle groups
          </td>
          <td className="py-1">
            {requirements.target_muscle_groups.map(formatEnum).join(", ")}
          </td>
        </tr>
        <tr>
          <td className="py-1 pr-4 text-muted-foreground font-medium">
            Equipment
          </td>
          <td className="py-1">
            {requirements.available_equipment.map(formatEnum).join(", ")}
          </td>
        </tr>
        {requirements.user_prompt && (
          <tr>
            <td className="py-1 pr-4 text-muted-foreground font-medium">
              Instructions
            </td>
            <td className="py-1">{requirements.user_prompt}</td>
          </tr>
        )}
      </tbody>
    </table>
  );
}
