"use client";

import { PageHeader } from "@/components/common/page-header";
import { useCurrentUser } from "@/hooks/queries/useCurrentUser";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";
import { useRouter } from "next/navigation";

export default function AccountPage() {
  const { data: user, isLoading, error } = useCurrentUser();
  const { logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <PageHeader title="Account" />
        <div className="space-y-2">
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <PageHeader title="Account" />
        <div className="text-center py-12">
          <p className="text-destructive">Failed to load account details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <PageHeader title="Account" />
      <div className="rounded-md border w-full max-w-md">
        <Table>
          <TableBody>
            <TableRow>
              <TableCell className="font-medium text-muted-foreground">
                Full name
              </TableCell>
              <TableCell>{user?.full_name}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell className="font-medium text-muted-foreground">
                Email
              </TableCell>
              <TableCell>{user?.email}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
      <div className="mt-8">
        <Button variant="destructive" onClick={handleLogout}>
          Log out
        </Button>
      </div>
    </div>
  );
}
