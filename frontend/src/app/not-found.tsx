import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <h2 className="text-4xl font-bold mb-4">404</h2>
      <p className="text-xl text-muted-foreground mb-6">Page not found</p>
      <p className="text-muted-foreground mb-8">
        The page you are looking for does not exist.
      </p>
      <Button asChild>
        <Link href="/">Return Home</Link>
      </Button>
    </div>
  );
}
