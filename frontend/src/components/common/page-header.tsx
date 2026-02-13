import { Button } from "@/components/ui/button";
import { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
  actionButton?: {
    label: string;
    onClick: () => void;
  };
}

export function PageHeader({
  title,
  description,
  actionButton,
}: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-8 pb-6 border-b-2 border-border/50">
      <div>
        <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
          {title}
        </h1>
        {description && (
          <p className="text-muted-foreground mt-3 text-base leading-relaxed">
            {description}
          </p>
        )}
      </div>
      {actionButton && (
        <Button
          onClick={actionButton.onClick}
          className="transition-all duration-200 hover:scale-105 hover:shadow-md px-6"
          size="lg"
        >
          {actionButton.label}
        </Button>
      )}
    </div>
  );
}
