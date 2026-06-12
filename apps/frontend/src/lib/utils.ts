import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getRiskColor(risk: string): string {
  switch (risk) {
    case "HIGH":
      return "text-cyber-red";
    case "MEDIUM":
      return "text-cyber-amber";
    case "LOW":
      return "text-cyber-green";
    default:
      return "text-muted-foreground";
  }
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case "CRITICAL":
      return "text-cyber-red";
    case "WARNING":
      return "text-cyber-amber";
    case "INFO":
      return "text-cyber-cyan";
    default:
      return "text-muted-foreground";
  }
}
