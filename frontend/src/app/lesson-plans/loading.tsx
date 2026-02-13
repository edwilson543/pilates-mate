import { PageHeader } from "@/components/common/page-header";
import { Skeleton } from "@/components/ui/skeleton";

export default function LessonPlansLoading() {
  return (
    <div className="p-8">
      <PageHeader title="Lesson plans" />
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {[...Array(6)].map((_, i) => (
          <Skeleton key={i} className="h-48" />
        ))}
      </div>
    </div>
  );
}
