"use client";

import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/common/app-sidebar";
import { AuthGuard } from "@/components/common/auth-guard";

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex h-screen">
        <SidebarProvider>
          <AppSidebar />
          <main className="w-full overflow-y-auto">{children}</main>
        </SidebarProvider>
      </div>
    </AuthGuard>
  );
}
