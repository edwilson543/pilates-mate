import { PageHeader } from "@/components/custom/page-header";
import { Skeleton } from "@/components/ui/skeleton";

export default function ExercisesLoading() {
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
