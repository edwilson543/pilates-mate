"use client";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from "@/components/ui/sidebar";
import { Dumbbell, FileText } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const menuItems = [
  {
    title: "Exercises",
    icon: Dumbbell,
    href: "/exercises",
  },
  {
    title: "Lesson plans",
    icon: FileText,
    href: "/lesson-plans",
  },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar className="border-r bg-gradient-to-b from-sidebar to-secondary/20">
      <SidebarContent className="pt-6">
        <SidebarGroup>
          <div className={"justify-items-center"}>
            <h1 className={"text-xl font-light"}>My pilates mate</h1>
          </div>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarMenu className="space-y-2 px-2">
            {menuItems.map((item) => {
              const isActive = pathname.startsWith(item.href);
              return (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={isActive}
                    className="transition-all duration-200 hover:scale-105 hover:shadow-md"
                  >
                    <Link href={item.href}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              );
            })}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
